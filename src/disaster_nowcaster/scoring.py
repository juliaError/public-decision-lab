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


class MissingIndicatorError(ValueError):
    """Raised when a score cannot be computed because required indicators are absent."""


def load_priority_config(path: str | Path) -> dict[str, Any]:
    """Load a priority-model YAML configuration.

    The file is expected to define `scores` with explicit weights. This function
    only parses YAML; it does not provide implicit default weights.
    """

    config_path = Path(path)
    with config_path.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)
    if not isinstance(config, dict):
        raise ValueError(f"{config_path} must contain a YAML mapping.")
    if "scores" not in config or not isinstance(config["scores"], dict):
        raise ValueError(f"{config_path} must define a `scores` mapping.")
    return config


def min_max_normalize(series: pd.Series) -> pd.Series:
    """Normalize a numeric series to the [0, 1] interval.

    Missing values remain missing. If all non-missing values are equal, the
    normalized value is `0.0`. This deterministic neutral-zero convention avoids
    creating artificial variation where the input provides none.
    """

    numeric = pd.to_numeric(series, errors="coerce")
    non_missing = numeric.dropna()
    if non_missing.empty:
        return pd.Series(DEFAULT_EQUAL_VALUE, index=series.index, dtype="float64")

    minimum = float(non_missing.min())
    maximum = float(non_missing.max())
    if maximum == minimum:
        normalized = pd.Series(DEFAULT_EQUAL_VALUE, index=series.index, dtype="float64")
        normalized[numeric.isna()] = pd.NA
        return normalized
    return (numeric - minimum) / (maximum - minimum)


def normalize_indicators(
    df: pd.DataFrame, indicators: list[str], method: str = "min_max"
) -> pd.DataFrame:
    """Return a copy of `df` with normalized indicator component columns.

    Component columns are named `{indicator}_normalized`. Missing indicator
    columns raise `MissingIndicatorError` so required data gaps are explicit.
    """

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
) -> pd.DataFrame:
    """Compute a transparent weighted additive score.

    The input `weights` mapping is the only source of weights. For each
    indicator, the function creates `{score_name}_component_{indicator}` using
    min-max-normalized indicator values multiplied by the indicator weight.

    Missing columns are never silently imputed:

    - `missing_policy="raise"` raises `MissingIndicatorError`.
    - `missing_policy="flag"` adds `{score_name}_missing_indicators` and leaves
      `{score_name}` as missing.
    - `missing_policy="skip"` computes from available indicators and renormalizes
      available weights to sum to one; callers should only use this for optional
      indicators and should report what was skipped.
    """

    _validate_weights(weights, score_name)
    missing = [indicator for indicator in weights if indicator not in df.columns]
    result = df.copy()
    if missing:
        result[f"{score_name}_missing_indicators"] = _join_indicators(missing)
        if missing_policy == "raise":
            raise MissingIndicatorError(
                f"{score_name} is missing required indicators: {', '.join(missing)}"
            )
        if missing_policy == "flag":
            result[score_name] = pd.NA
            return result
        if missing_policy != "skip":
            raise ValueError(f"Unsupported missing policy: {missing_policy!r}.")

    available_weights = {
        indicator: weight
        for indicator, weight in weights.items()
        if indicator in result.columns
    }
    if not available_weights:
        result[score_name] = pd.NA
        return result

    weight_total = float(sum(available_weights.values()))
    if weight_total <= 0:
        raise ValueError(f"{score_name} weights must sum to a positive value.")

    score = pd.Series(0.0, index=result.index, dtype="float64")
    for indicator, weight in available_weights.items():
        component_name = f"{score_name}_component_{indicator}"
        normalized = min_max_normalize(result[indicator])
        component = normalized.fillna(0.0) * (float(weight) / weight_total)
        result[component_name] = component
        score = score + component
    result[score_name] = score
    result[f"{score_name}_weight_sum_used"] = weight_total
    if f"{score_name}_missing_indicators" not in result.columns:
        result[f"{score_name}_missing_indicators"] = ""
    return result


def compute_priority_scores(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    """Compute all score families defined in a priority-model configuration.

    Required indicators must exist. Optional indicators may be absent; they are
    skipped with score-specific missing-indicator flags. This function supports
    weighted additive scores and a simple road-repair `benefit_over_cost` score.
    """

    scores = config.get("scores", {})
    if not isinstance(scores, dict):
        raise ValueError("Priority config must contain a `scores` mapping.")

    normalization = config.get("normalization", {})
    missing_policy = str(normalization.get("missing_value_policy", "flag"))
    result = df.copy()

    for score_name, score_config in scores.items():
        if not isinstance(score_config, dict):
            raise ValueError(f"{score_name} score config must be a mapping.")
        if score_config.get("formula") == "benefit_over_cost":
            result = _compute_benefit_over_cost_score(result, score_name, score_config)
        else:
            result = _compute_configured_weighted_score(
                result, score_name, score_config, missing_policy=missing_policy
            )
    return result


def assign_data_quality_flags(
    df: pd.DataFrame,
    required_indicators: list[str],
    optional_indicators: list[str] | None = None,
) -> pd.DataFrame:
    """Assign row-level data quality flags for required and optional indicators.

    Flags use four values:

    - `high`: no required or optional indicators are missing;
    - `medium`: required indicators are present, but at least one optional
      indicator is missing;
    - `low`: some required indicators are missing;
    - `insufficient`: all required indicators are missing.
    """

    optional_indicators = optional_indicators or []
    result = df.copy()
    missing_required: list[list[str]] = []
    missing_optional: list[list[str]] = []
    flags: list[str] = []

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
        if required_indicators and len(required_missing) == len(required_indicators):
            flags.append(QUALITY_INSUFFICIENT)
        elif required_missing:
            flags.append(QUALITY_LOW)
        elif optional_missing:
            flags.append(QUALITY_MEDIUM)
        else:
            flags.append(QUALITY_HIGH)

    result["missing_required_indicators"] = [
        _join_indicators(items) for items in missing_required
    ]
    result["missing_optional_indicators"] = [
        _join_indicators(items) for items in missing_optional
    ]
    result["data_quality_flag"] = flags
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
    missing_policy: str,
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

    missing_optional_columns = [
        indicator for indicator in optional if indicator not in df.columns
    ]
    available_weights = {
        indicator: weight
        for indicator, weight in weights.items()
        if indicator in df.columns and indicator not in missing_optional_columns
    }
    result = compute_weighted_score(
        df, available_weights, score_name, missing_policy=missing_policy
    )
    result[f"{score_name}_missing_optional_indicators"] = _join_indicators(
        missing_optional_columns
    )
    result[f"{score_name}_missing_required_indicators"] = ""
    result[f"{score_name}_data_quality_flag"] = (
        QUALITY_MEDIUM if missing_optional_columns else QUALITY_HIGH
    )
    return result


def _compute_benefit_over_cost_score(
    df: pd.DataFrame, score_name: str, score_config: dict[str, Any]
) -> pd.DataFrame:
    benefit_weights = _weights_from_config(score_config, score_name, key="benefit_weights")
    required = list(score_config.get("required_indicators", benefit_weights.keys()))
    optional = list(score_config.get("optional_indicators", []))
    cost_terms = list(score_config.get("cost_terms", []))
    missing_required = [indicator for indicator in required if indicator not in df.columns]
    if missing_required:
        raise MissingIndicatorError(
            f"{score_name} is missing required indicators: {', '.join(missing_required)}"
        )

    missing_optional = [indicator for indicator in optional if indicator not in df.columns]
    available_benefit_weights = {
        indicator: weight
        for indicator, weight in benefit_weights.items()
        if indicator in df.columns
    }
    result = compute_weighted_score(
        df, available_benefit_weights, f"{score_name}_benefit", missing_policy="raise"
    )
    cost_score = pd.Series(0.0, index=result.index, dtype="float64")
    available_cost_terms = [term for term in cost_terms if term in result.columns]
    if available_cost_terms:
        for term in available_cost_terms:
            component_name = f"{score_name}_cost_component_{term}"
            component = min_max_normalize(result[term]).fillna(0.0)
            result[component_name] = component
            cost_score = cost_score + component
        cost_score = cost_score / len(available_cost_terms)
    result[f"{score_name}_cost_index"] = cost_score
    result[score_name] = result[f"{score_name}_benefit"] / (1.0 + cost_score)
    result[f"{score_name}_missing_optional_indicators"] = _join_indicators(
        missing_optional
    )
    result[f"{score_name}_missing_required_indicators"] = ""
    result[f"{score_name}_data_quality_flag"] = (
        QUALITY_MEDIUM if missing_optional else QUALITY_HIGH
    )
    return result


def _weights_from_config(
    score_config: dict[str, Any], score_name: str, key: str
) -> dict[str, float]:
    weights = score_config.get(key)
    if not isinstance(weights, dict) or not weights:
        raise ValueError(f"{score_name} must define a non-empty `{key}` mapping.")
    return {str(indicator): float(weight) for indicator, weight in weights.items()}


def _validate_weights(weights: dict[str, float], score_name: str) -> None:
    if not weights:
        raise ValueError(f"{score_name} requires at least one explicit weight.")
    if any(float(weight) < 0 for weight in weights.values()):
        raise ValueError(f"{score_name} weights must be non-negative.")
    if sum(float(weight) for weight in weights.values()) <= 0:
        raise ValueError(f"{score_name} weights must sum to a positive value.")


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
