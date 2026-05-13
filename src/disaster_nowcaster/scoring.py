"""Transparent priority scoring utilities.

This module has two layers:

- `build_priority_rows` preserves the static v0.1 demo ranking used by the
  current CLI report.
- The pandas/YAML functions implement configurable, action-specific priority
  indices. They do not contain hidden weights; every weighted score must receive
  weights from a caller-provided configuration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from disaster_nowcaster.geometry import extract_polygons, geometry_intersects_any_polygon
from disaster_nowcaster.schemas import Feature, GeoJSONLayer, PriorityRow

NORMALIZED_SUFFIX = "_normalized"
DEFAULT_EQUAL_VALUE = 0.0
QUALITY_HIGH = "high"
QUALITY_MEDIUM = "medium"
QUALITY_LOW = "low"
QUALITY_INSUFFICIENT = "insufficient"
COMPLETENESS_COMPLETE = "complete"
COMPLETENESS_OPTIONAL_MISSING = "optional_missing"
COMPLETENESS_REQUIRED_MISSING = "required_missing"
COMPLETENESS_INSUFFICIENT = "insufficient"
VALID_ENTITY_LEVELS = {"admin_area", "grid_cell", "road_segment", "facility", "event"}
VALID_DIRECTIONS = {
    "higher_is_worse",
    "higher_is_better",
    "higher_is_costlier",
    "lower_is_worse",
}
VALID_ROLES = {
    "hazard",
    "exposure",
    "vulnerability",
    "capacity",
    "lifeline",
    "feasibility",
    "cost",
    "benefit",
    "field_report",
}
VALID_FORMULAS = {"benefit_over_cost", "need_with_feasibility_warning"}
WEIGHT_TOLERANCE = 1e-6


class MissingIndicatorError(ValueError):
    """Raised when a score cannot be computed because required indicators are absent."""


class ConfigValidationError(ValueError):
    """Raised when a priority-model configuration is structurally unsafe."""


def load_priority_config(path: str | Path) -> dict[str, Any]:
    """Load and validate a priority-model YAML configuration."""

    config_path = Path(path)
    with config_path.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)
    if not isinstance(config, dict):
        raise ValueError(f"{config_path} must contain a YAML mapping.")
    validate_priority_config(config)
    return config


def validate_priority_config(config: dict[str, Any]) -> None:
    """Validate semantic safety rules for a priority-model configuration.

    Validation checks required top-level keys, score entities, indicator catalog
    coverage, indicator directions and entity levels, non-negative weights, and
    weight sums for weighted score families.
    """

    for key in ["model", "normalization", "indicator_catalog", "scores", "reporting"]:
        if key not in config:
            raise ConfigValidationError(f"Priority config is missing top-level key: {key}")

    catalog = config["indicator_catalog"]
    scores = config["scores"]
    if not isinstance(catalog, dict) or not catalog:
        raise ConfigValidationError("indicator_catalog must be a non-empty mapping.")
    if not isinstance(scores, dict) or not scores:
        raise ConfigValidationError("scores must be a non-empty mapping.")

    for indicator, metadata in catalog.items():
        _validate_indicator_metadata(str(indicator), metadata)

    for score_name, score_config in scores.items():
        if not isinstance(score_config, dict):
            raise ConfigValidationError(f"{score_name} score config must be a mapping.")
        entity = score_config.get("entity")
        if entity not in VALID_ENTITY_LEVELS:
            raise ConfigValidationError(f"{score_name} has invalid entity: {entity!r}.")

        formula = score_config.get("formula")
        if formula is not None and formula not in VALID_FORMULAS:
            raise ConfigValidationError(f"{score_name} has invalid formula: {formula!r}.")

        if formula == "benefit_over_cost":
            _validate_weight_mapping(score_name, score_config, "benefit_weights")
            _validate_score_indicators(score_name, score_config, catalog)
            continue
        if formula == "need_with_feasibility_warning":
            _validate_derived_score_references(score_name, score_config, scores)
            continue

        _validate_weight_mapping(score_name, score_config, "weights")
        _validate_score_indicators(score_name, score_config, catalog)


def min_max_normalize(series: pd.Series) -> pd.Series:
    """Normalize a numeric series to the [0, 1] interval.

    Missing values remain missing. If all non-missing values are equal, the
    normalized value is `0.0`. This is a zero discriminatory contribution:
    the indicator provides no within-event ranking information. It does not
    mean the underlying risk, need, cost, or benefit is zero.
    """

    numeric = pd.to_numeric(series, errors="coerce")
    non_missing = numeric.dropna()
    if non_missing.empty:
        return pd.Series(pd.NA, index=series.index, dtype="Float64")

    minimum = float(non_missing.min())
    maximum = float(non_missing.max())
    if maximum == minimum:
        normalized = pd.Series(DEFAULT_EQUAL_VALUE, index=series.index, dtype="float64")
        normalized[numeric.isna()] = pd.NA
        return normalized
    return (numeric - minimum) / (maximum - minimum)


def normalize_indicator(
    series: pd.Series, direction: str = "higher_is_worse"
) -> pd.Series:
    """Normalize an indicator and orient it so higher normalized values raise the score."""

    if direction not in VALID_DIRECTIONS:
        raise ValueError(f"Unsupported indicator direction: {direction!r}.")
    normalized = min_max_normalize(series)
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if not numeric.empty and float(numeric.min()) == float(numeric.max()):
        return normalized
    if direction == "lower_is_worse":
        return 1.0 - normalized
    return normalized


def normalize_indicators(
    df: pd.DataFrame, indicators: list[str], method: str = "min_max"
) -> pd.DataFrame:
    """Return a copy of `df` with normalized indicator component columns."""

    missing = [indicator for indicator in indicators if indicator not in df.columns]
    if missing:
        raise MissingIndicatorError(
            f"Missing indicator columns for normalization: {', '.join(missing)}"
        )
    if method != "min_max":
        raise ValueError(f"Unsupported normalization method: {method!r}.")

    result = df.copy()
    for indicator in indicators:
        result[_normalized_name(indicator)] = min_max_normalize(result[indicator])
    return result


def compute_weighted_score(
    df: pd.DataFrame,
    weights: dict[str, float],
    score_name: str,
    missing_policy: str = "flag",
    indicator_directions: dict[str, str] | None = None,
    required_indicators: list[str] | None = None,
    optional_indicators: list[str] | None = None,
) -> pd.DataFrame:
    """Compute a transparent weighted additive score.

    The input `weights` mapping is the only source of weights. Optional missing
    columns are skipped and available weights are renormalized when
    `missing_policy="skip"`. Missing required row values make that row's score
    missing and set row-level quality/completeness flags.
    """

    _validate_weights(weights, score_name, require_sum_one=False)
    indicator_directions = indicator_directions or {}
    required_indicators = required_indicators or list(weights.keys())
    optional_indicators = optional_indicators or []
    missing_required_columns = [
        indicator for indicator in required_indicators if indicator not in df.columns
    ]
    result = df.copy()

    if missing_required_columns:
        result[f"{score_name}_missing_required_indicators"] = _join_indicators(
            missing_required_columns
        )
        if missing_policy == "raise":
            raise MissingIndicatorError(
                f"{score_name} is missing required indicators: "
                f"{', '.join(missing_required_columns)}"
            )
        if missing_policy == "flag":
            result[score_name] = pd.NA
            result[f"{score_name}_data_quality_flag"] = QUALITY_INSUFFICIENT
            result[f"{score_name}_model_completeness_flag"] = COMPLETENESS_INSUFFICIENT
            return result
        if missing_policy != "skip":
            raise ValueError(f"Unsupported missing policy: {missing_policy!r}.")

    optional_missing_columns = [
        indicator for indicator in optional_indicators if indicator not in result.columns
    ]
    available_weights = {
        indicator: weight
        for indicator, weight in weights.items()
        if indicator in result.columns and indicator not in optional_missing_columns
    }
    if not available_weights:
        result[score_name] = pd.NA
        result[f"{score_name}_missing_required_indicators"] = _join_indicators(
            missing_required_columns
        )
        result[f"{score_name}_missing_optional_indicators"] = _join_indicators(
            optional_missing_columns
        )
        if optional_missing_columns and not missing_required_columns:
            result[f"{score_name}_data_quality_flag"] = QUALITY_MEDIUM
            result[f"{score_name}_model_completeness_flag"] = (
                COMPLETENESS_OPTIONAL_MISSING
            )
        else:
            result[f"{score_name}_data_quality_flag"] = QUALITY_INSUFFICIENT
            result[f"{score_name}_model_completeness_flag"] = (
                COMPLETENESS_INSUFFICIENT
            )
        return result

    weight_total = float(sum(available_weights.values()))
    if weight_total <= 0:
        raise ValueError(f"{score_name} weights must sum to a positive value.")

    score_numerator = pd.Series(0.0, index=result.index, dtype="float64")
    row_weight_total = pd.Series(0.0, index=result.index, dtype="float64")
    required_missing_by_row: list[list[str]] = []
    optional_missing_by_row: list[list[str]] = []
    for _, row in result.iterrows():
        required_missing = [
            indicator
            for indicator in required_indicators
            if indicator not in result.columns or pd.isna(row.get(indicator))
        ]
        optional_missing = [
            indicator
            for indicator in optional_indicators
            if indicator not in result.columns or pd.isna(row.get(indicator))
        ]
        required_missing_by_row.append(required_missing)
        optional_missing_by_row.append(optional_missing)

    for indicator, weight in available_weights.items():
        component_name = f"{score_name}_component_{indicator}"
        direction = indicator_directions.get(indicator, "higher_is_worse")
        normalized = normalize_indicator(result[indicator], direction=direction)
        available_mask = normalized.notna()
        row_weight_total = row_weight_total + available_mask.astype(float) * float(weight)
        component = normalized.fillna(0.0) * float(weight)
        result[component_name] = component
        score_numerator = score_numerator + component

    required_missing_mask = pd.Series(
        [bool(items) for items in required_missing_by_row], index=result.index
    )
    score = score_numerator / row_weight_total.replace(0.0, pd.NA)
    result[score_name] = score.mask(required_missing_mask, pd.NA)
    result[f"{score_name}_weight_sum_used"] = weight_total
    result[f"{score_name}_row_weight_sum_used"] = row_weight_total.mask(
        required_missing_mask, pd.NA
    )
    result[f"{score_name}_missing_required_indicators"] = [
        _join_indicators(items) for items in required_missing_by_row
    ]
    result[f"{score_name}_missing_optional_indicators"] = [
        _join_indicators(sorted(set(items + optional_missing_columns)))
        for items in optional_missing_by_row
    ]
    flags = _flags_from_missing_lists(
        required_missing_by_row,
        optional_missing_by_row,
        required_count=len(required_indicators),
    )
    result[f"{score_name}_data_quality_flag"] = flags["data_quality"]
    result[f"{score_name}_model_completeness_flag"] = flags["model_completeness"]
    return result


def compute_priority_scores(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Compute all score families defined in a validated priority-model config."""

    validate_priority_config(config)
    scores = config["scores"]
    result = df.copy()
    indicator_directions = _indicator_directions(config)

    for score_name, score_config in scores.items():
        if score_config.get("formula") == "benefit_over_cost":
            result = _compute_benefit_over_cost_score(
                result, score_name, score_config, indicator_directions
            )
        elif score_config.get("formula") == "need_with_feasibility_warning":
            result = _compute_need_with_feasibility_warning(result, score_name, score_config)
        else:
            result = _compute_configured_weighted_score(
                result, score_name, score_config, indicator_directions
            )
        result[f"{score_name}_entity"] = str(score_config["entity"])
    return result


def assign_data_quality_flags(
    df: pd.DataFrame,
    required_indicators: list[str],
    optional_indicators: list[str] | None = None,
) -> pd.DataFrame:
    """Assign row-level data-quality and model-completeness flags."""

    optional_indicators = optional_indicators or []
    result = df.copy()
    missing_required: list[list[str]] = []
    missing_optional: list[list[str]] = []

    for _, row in result.iterrows():
        required_missing = [
            indicator
            for indicator in required_indicators
            if indicator not in result.columns or pd.isna(row.get(indicator))
        ]
        optional_missing = [
            indicator
            for indicator in optional_indicators
            if indicator not in result.columns or pd.isna(row.get(indicator))
        ]
        missing_required.append(required_missing)
        missing_optional.append(optional_missing)

    flags = _flags_from_missing_lists(
        missing_required, missing_optional, required_count=len(required_indicators)
    )
    result["missing_required_indicators"] = [
        _join_indicators(items) for items in missing_required
    ]
    result["missing_optional_indicators"] = [
        _join_indicators(items) for items in missing_optional
    ]
    result["data_quality_flag"] = flags["data_quality"]
    result["model_completeness_flag"] = flags["model_completeness"]
    return result


def build_priority_rows(
    admin: GeoJSONLayer,
    affected_roads: list[Feature],
    affected_facilities: list[Feature],
    exposed_population_by_admin: list[PriorityRow] | None = None,
) -> list[PriorityRow]:
    """Build admin-level demo priority rows from exposed infrastructure counts.

    The v0.1 score is a transparent sorting aid:
    affected road count + affected facility count. It is not an official
    allocation decision and does not represent confirmed damage.
    """

    population_lookup = {
        str(row["admin_id"]): row for row in (exposed_population_by_admin or [])
    }
    rows: list[PriorityRow] = []
    for index, feature in enumerate(admin.features, start=1):
        polygons = extract_polygons(feature["geometry"])
        road_count = _count_features_in_polygons(affected_roads, polygons)
        facility_count = _count_features_in_polygons(affected_facilities, polygons)
        score = road_count + facility_count
        properties = feature.get("properties", {})
        admin_id = properties.get("id", f"admin_{index}")
        population_row = population_lookup.get(str(admin_id), {})
        rows.append(
            {
                "admin_id": admin_id,
                "admin_name": properties.get("name", f"Admin unit {index}"),
                "potentially_affected_road_count": road_count,
                "facilities_within_hazard_extent_count": facility_count,
                "estimated_exposed_population": float(
                    population_row.get("estimated_exposed_population", 0.0)
                ),
                "demo_priority_score": score,
                "demo_rank": 0,
                "interpretation": (
                    "Decision-support sorting aid only; exposure count, not confirmed damage."
                ),
            }
        )

    rows.sort(
        key=lambda row: (
            -row["demo_priority_score"],
            -row["facilities_within_hazard_extent_count"],
            -row["potentially_affected_road_count"],
            str(row["admin_name"]),
        )
    )
    for rank, row in enumerate(rows, start=1):
        row["demo_rank"] = rank
    return rows


def _compute_configured_weighted_score(
    df: pd.DataFrame,
    score_name: str,
    score_config: dict[str, Any],
    indicator_directions: dict[str, str],
) -> pd.DataFrame:
    weights = _weights_from_config(score_config, score_name, key="weights")
    required = list(score_config.get("required_indicators", weights.keys()))
    optional = list(score_config.get("optional_indicators", []))
    missing_required_columns = [
        indicator for indicator in required if indicator not in df.columns
    ]
    if missing_required_columns:
        raise MissingIndicatorError(
            f"{score_name} is missing required indicators: "
            f"{', '.join(missing_required_columns)}"
        )

    return compute_weighted_score(
        df,
        weights,
        score_name,
        missing_policy="skip",
        indicator_directions=indicator_directions,
        required_indicators=required,
        optional_indicators=optional,
    )


def _compute_need_with_feasibility_warning(
    df: pd.DataFrame, score_name: str, score_config: dict[str, Any]
) -> pd.DataFrame:
    result = df.copy()
    need_score = str(score_config["need_score"])
    feasibility_score = str(score_config["feasibility_score"])
    if need_score not in result.columns:
        raise MissingIndicatorError(f"{score_name} requires computed score: {need_score}")
    result[score_name] = result[need_score]
    result[f"{score_name}_need_component"] = result[need_score]
    if feasibility_score in result.columns:
        result[f"{score_name}_feasibility_component"] = result[feasibility_score]
        missing_optional = result.get(
            f"{feasibility_score}_missing_optional_indicators",
            pd.Series("", index=result.index),
        )
    else:
        result[f"{score_name}_feasibility_component"] = pd.NA
        missing_optional = pd.Series(feasibility_score, index=result.index)

    result[f"{score_name}_warning"] = str(score_config.get("warning", ""))
    result[f"{score_name}_missing_required_indicators"] = result.get(
        f"{need_score}_missing_required_indicators", ""
    )
    result[f"{score_name}_missing_optional_indicators"] = missing_optional
    result[f"{score_name}_data_quality_flag"] = result.get(
        f"{need_score}_data_quality_flag", QUALITY_HIGH
    )
    result[f"{score_name}_model_completeness_flag"] = result.get(
        f"{need_score}_model_completeness_flag", COMPLETENESS_COMPLETE
    )
    return result


def _compute_benefit_over_cost_score(
    df: pd.DataFrame,
    score_name: str,
    score_config: dict[str, Any],
    indicator_directions: dict[str, str],
) -> pd.DataFrame:
    benefit_weights = _weights_from_config(score_config, score_name, key="benefit_weights")
    required = list(score_config.get("required_indicators", benefit_weights.keys()))
    optional = list(score_config.get("optional_indicators", []))
    cost_terms = list(score_config.get("cost_terms", []))
    missing_required_columns = [
        indicator for indicator in required if indicator not in df.columns
    ]
    if missing_required_columns:
        raise MissingIndicatorError(
            f"{score_name} is missing required indicators: "
            f"{', '.join(missing_required_columns)}"
        )

    cost_required_terms = [
        indicator
        for indicator in required
        if indicator in cost_terms and indicator not in benefit_weights
    ]
    result = compute_weighted_score(
        df,
        benefit_weights,
        f"{score_name}_benefit",
        missing_policy="skip",
        indicator_directions=indicator_directions,
        required_indicators=[
            indicator for indicator in required if indicator in benefit_weights
        ],
        optional_indicators=[
            indicator for indicator in optional if indicator in benefit_weights
        ],
    )
    benefit_index = str(
        score_config.get("benefit_index", f"{score_name}_benefit_index")
    )
    cost_index = str(score_config.get("cost_index", f"{score_name}_cost_index"))
    result[benefit_index] = result[f"{score_name}_benefit"]

    available_cost_terms = [term for term in cost_terms if term in result.columns]
    missing_cost_terms = [term for term in cost_terms if term not in result.columns]
    cost_score = pd.Series(0.0, index=result.index, dtype="float64")
    if available_cost_terms:
        for term in available_cost_terms:
            component_name = f"{score_name}_cost_component_{term}"
            direction = indicator_directions.get(term, "higher_is_costlier")
            component = normalize_indicator(result[term], direction=direction).fillna(0.0)
            result[component_name] = component
            cost_score = cost_score + component
        cost_score = cost_score / len(available_cost_terms)

    epsilon = float(score_config.get("epsilon", 1.0))
    if epsilon <= 0:
        raise ValueError(f"{score_name} epsilon must be positive.")
    cost_required_missing_by_row: list[list[str]] = []
    for _, row in result.iterrows():
        cost_required_missing_by_row.append(
            [
                indicator
                for indicator in cost_required_terms
                if indicator not in result.columns or pd.isna(row.get(indicator))
            ]
        )
    required_cost_missing_mask = pd.Series(
        [bool(items) for items in cost_required_missing_by_row], index=result.index
    )
    result[cost_index] = cost_score
    result[score_name] = (result[benefit_index] / (epsilon + cost_score)).mask(
        required_cost_missing_mask, pd.NA
    )
    result[f"{score_name}_epsilon"] = epsilon
    result[f"{score_name}_missing_cost_terms"] = _join_indicators(missing_cost_terms)
    benefit_required = result.get(
        f"{score_name}_benefit_missing_required_indicators",
        pd.Series("", index=result.index),
    )
    result[f"{score_name}_missing_required_indicators"] = [
        _join_indicators([item for item in str(left).split(",") if item] + right)
        for left, right in zip(benefit_required, cost_required_missing_by_row)
    ]
    result[f"{score_name}_missing_optional_indicators"] = result.get(
        f"{score_name}_benefit_missing_optional_indicators", ""
    )
    if missing_cost_terms:
        existing = result[f"{score_name}_missing_optional_indicators"].astype(str)
        appended = existing.apply(
            lambda value: _join_indicators(
                [item for item in value.split(",") if item] + missing_cost_terms
            )
        )
        result[f"{score_name}_missing_optional_indicators"] = appended
    flags = _flags_from_missing_lists(
        [
            [item for item in str(value).split(",") if item]
            for value in result[f"{score_name}_missing_required_indicators"]
        ],
        [
            [item for item in str(value).split(",") if item]
            for value in result[f"{score_name}_missing_optional_indicators"]
        ],
        required_count=len(required),
    )
    result[f"{score_name}_data_quality_flag"] = flags["data_quality"]
    result[f"{score_name}_model_completeness_flag"] = flags["model_completeness"]
    return result


def _validate_indicator_metadata(indicator: str, metadata: Any) -> None:
    if not isinstance(metadata, dict):
        raise ConfigValidationError(f"{indicator} metadata must be a mapping.")
    required_keys = [
        "concept",
        "entity_level",
        "direction",
        "role",
        "unit",
        "interpretation_note",
        "sensitivity_privacy_note",
    ]
    for key in required_keys:
        if key not in metadata:
            raise ConfigValidationError(f"{indicator} is missing metadata key: {key}")
    if metadata["entity_level"] not in VALID_ENTITY_LEVELS:
        raise ConfigValidationError(
            f"{indicator} has invalid entity_level: {metadata['entity_level']!r}."
        )
    if metadata["direction"] not in VALID_DIRECTIONS:
        raise ConfigValidationError(
            f"{indicator} has invalid direction: {metadata['direction']!r}."
        )
    if metadata["role"] not in VALID_ROLES:
        raise ConfigValidationError(
            f"{indicator} has invalid role: {metadata['role']!r}."
        )


def _validate_weight_mapping(
    score_name: str, score_config: dict[str, Any], key: str
) -> None:
    weights = _weights_from_config(score_config, score_name, key=key)
    _validate_weights(weights, score_name, require_sum_one=True)


def _validate_score_indicators(
    score_name: str, score_config: dict[str, Any], catalog: dict[str, Any]
) -> None:
    indicator_names: list[str] = []
    for key in ["weights", "benefit_weights"]:
        if isinstance(score_config.get(key), dict):
            indicator_names.extend(str(item) for item in score_config[key])
    indicator_names.extend(str(item) for item in score_config.get("required_indicators", []))
    indicator_names.extend(str(item) for item in score_config.get("optional_indicators", []))
    indicator_names.extend(str(item) for item in score_config.get("cost_terms", []))
    for indicator in sorted(set(indicator_names)):
        if indicator not in catalog:
            raise ConfigValidationError(
                f"{score_name} uses indicator not defined in catalog: {indicator}"
            )


def _validate_derived_score_references(
    score_name: str, score_config: dict[str, Any], scores: dict[str, Any]
) -> None:
    for key in ["need_score", "feasibility_score"]:
        reference = score_config.get(key)
        if reference not in scores:
            raise ConfigValidationError(
                f"{score_name} references unknown {key}: {reference!r}."
            )


def _weights_from_config(
    score_config: dict[str, Any], score_name: str, key: str
) -> dict[str, float]:
    weights = score_config.get(key)
    if not isinstance(weights, dict) or not weights:
        raise ValueError(f"{score_name} must define a non-empty `{key}` mapping.")
    return {str(indicator): float(weight) for indicator, weight in weights.items()}


def _validate_weights(
    weights: dict[str, float], score_name: str, require_sum_one: bool
) -> None:
    if not weights:
        raise ValueError(f"{score_name} requires at least one explicit weight.")
    if any(float(weight) < 0 for weight in weights.values()):
        raise ConfigValidationError(f"{score_name} weights must be non-negative.")
    weight_sum = sum(float(weight) for weight in weights.values())
    if weight_sum <= 0:
        raise ConfigValidationError(f"{score_name} weights must sum to a positive value.")
    if require_sum_one and abs(weight_sum - 1.0) > WEIGHT_TOLERANCE:
        raise ConfigValidationError(f"{score_name} weights must sum to one.")


def _indicator_directions(config: dict[str, Any]) -> dict[str, str]:
    return {
        str(indicator): str(metadata["direction"])
        for indicator, metadata in config["indicator_catalog"].items()
    }


def _flags_from_missing_lists(
    missing_required: list[list[str]],
    missing_optional: list[list[str]],
    required_count: int,
) -> dict[str, list[str]]:
    quality_flags: list[str] = []
    completeness_flags: list[str] = []
    for required_missing, optional_missing in zip(missing_required, missing_optional):
        if required_missing and required_count and len(required_missing) >= required_count:
            quality_flags.append(QUALITY_INSUFFICIENT)
            completeness_flags.append(COMPLETENESS_INSUFFICIENT)
        elif required_missing:
            quality_flags.append(QUALITY_LOW)
            completeness_flags.append(COMPLETENESS_REQUIRED_MISSING)
        elif optional_missing:
            quality_flags.append(QUALITY_MEDIUM)
            completeness_flags.append(COMPLETENESS_OPTIONAL_MISSING)
        else:
            quality_flags.append(QUALITY_HIGH)
            completeness_flags.append(COMPLETENESS_COMPLETE)
    return {
        "data_quality": quality_flags,
        "model_completeness": completeness_flags,
    }


def _normalized_name(indicator: str) -> str:
    return f"{indicator}{NORMALIZED_SUFFIX}"


def _join_indicators(indicators: list[str]) -> str:
    return ",".join(indicators)


def _count_features_in_polygons(features: list[Feature], polygons: list) -> int:
    return sum(
        1
        for feature in features
        if geometry_intersects_any_polygon(feature["geometry"], polygons)
    )
