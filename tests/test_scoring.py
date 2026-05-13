from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest

from disaster_nowcaster.scoring import (
    ConfigValidationError,
    MissingIndicatorError,
    assign_data_quality_flags,
    compute_priority_scores,
    compute_weighted_score,
    load_priority_config,
    min_max_normalize,
    normalize_indicator,
    normalize_indicators,
    validate_priority_config,
)


CONFIG_PATH = Path("configs/priority_models/baseline_flood.yml")


def test_min_max_normalization_scales_to_unit_interval():
    values = pd.Series([0, 5, 10])

    normalized = min_max_normalize(values)

    assert normalized.tolist() == [0.0, 0.5, 1.0]


def test_equal_value_normalization_returns_zero_discriminatory_contribution():
    values = pd.Series([3, 3, 3])

    normalized = min_max_normalize(values)

    assert normalized.tolist() == [0.0, 0.0, 0.0]


def test_direction_handling_orients_lower_is_worse():
    values = pd.Series([1, 5, 9])

    normalized = normalize_indicator(values, direction="lower_is_worse")

    assert normalized.tolist() == [1.0, 0.5, 0.0]


def test_equal_lower_is_worse_still_has_zero_discriminatory_contribution():
    values = pd.Series([4, 4, 4])

    normalized = normalize_indicator(values, direction="lower_is_worse")

    assert normalized.tolist() == [0.0, 0.0, 0.0]


def test_normalize_indicators_adds_component_columns():
    df = pd.DataFrame({"hazard": [1, 3], "exposure": [10, 20]})

    result = normalize_indicators(df, ["hazard", "exposure"])

    assert result["hazard_normalized"].tolist() == [0.0, 1.0]
    assert result["exposure_normalized"].tolist() == [0.0, 1.0]


def test_weighted_score_calculation_uses_explicit_weights():
    df = pd.DataFrame({"hazard": [0, 10], "exposure": [10, 0]})

    result = compute_weighted_score(
        df,
        weights={"hazard": 0.75, "exposure": 0.25},
        score_name="need_review",
        missing_policy="raise",
    )

    assert result["need_review"].tolist() == [0.25, 0.75]
    assert result["need_review_component_hazard"].tolist() == [0.0, 0.75]
    assert result["need_review_component_exposure"].tolist() == [0.25, 0.0]


def test_config_validation_success():
    config = load_priority_config(CONFIG_PATH)

    validate_priority_config(config)


def test_config_validation_failure_for_negative_weights():
    config = load_priority_config(CONFIG_PATH)
    config = deepcopy(config)
    config["scores"]["need_severity"]["weights"]["hazard_severity"] = -0.1

    with pytest.raises(ConfigValidationError, match="non-negative"):
        validate_priority_config(config)


def test_config_validation_failure_for_unknown_indicators():
    config = load_priority_config(CONFIG_PATH)
    config = deepcopy(config)
    value = config["scores"]["need_severity"]["weights"].pop("hazard_severity")
    config["scores"]["need_severity"]["weights"]["unknown_indicator"] = value
    config["scores"]["need_severity"]["required_indicators"] = [
        "unknown_indicator",
        "exposed_population",
        "vulnerability",
        "lack_of_coping_capacity",
    ]

    with pytest.raises(ConfigValidationError, match="not defined in catalog"):
        validate_priority_config(config)


def test_config_validation_failure_for_weights_not_summing_to_one():
    config = load_priority_config(CONFIG_PATH)
    config = deepcopy(config)
    config["scores"]["need_severity"]["weights"]["hazard_severity"] = 0.50

    with pytest.raises(ConfigValidationError, match="sum to one"):
        validate_priority_config(config)


def test_derived_score_role_is_validated():
    config = load_priority_config(CONFIG_PATH)

    assert config["indicator_catalog"]["need_severity"]["role"] == "derived_score"
    validate_priority_config(config)


def test_config_validation_failure_for_incompatible_entity_level():
    config = load_priority_config(CONFIG_PATH)
    config = deepcopy(config)
    config["indicator_catalog"]["vulnerability"]["entity_level"] = "road_segment"

    with pytest.raises(ConfigValidationError, match="incompatible entity"):
        validate_priority_config(config)


def test_config_validation_failure_for_weight_declaration_mismatch():
    config = load_priority_config(CONFIG_PATH)
    config = deepcopy(config)
    config["scores"]["need_severity"]["optional_indicators"] = []
    config["scores"]["need_severity"]["required_indicators"] = [
        "hazard_severity",
        "exposed_population",
        "lack_of_coping_capacity",
    ]

    with pytest.raises(ConfigValidationError, match="must match weights"):
        validate_priority_config(config)


def test_missing_required_indicator_columns_raise_explicit_error():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe().drop(columns=["hazard_severity"])

    with pytest.raises(MissingIndicatorError, match="hazard_severity"):
        compute_priority_scores(df, config)


def test_required_columns_present_but_row_values_missing_are_flagged():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe()
    df.loc[1, "hazard_severity"] = None

    result = compute_priority_scores(df, config)

    assert pd.isna(result.loc[1, "need_severity"])
    assert result.loc[1, "need_severity_missing_required_indicators"] == (
        "hazard_severity"
    )
    assert result.loc[1, "need_severity_data_quality_flag"] == "low"
    assert result.loc[1, "need_severity_model_completeness_flag"] == (
        "required_missing"
    )


def test_optional_missing_indicators_are_flagged_and_skipped():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe().drop(
        columns=[
            "energy_disruption",
            "field_distress_signal",
            "livelihood_loss_proxy",
            "delivery_feasibility",
            "alternative_health_access_loss",
            "repair_difficulty",
            "aid_route_importance",
        ]
    )

    result = compute_priority_scores(df, config)

    assert "need_severity" in result.columns
    assert result["lifeline_disruption_missing_optional_indicators"].iloc[0] == (
        "energy_disruption"
    )
    assert result["rescue_priority_missing_optional_indicators"].iloc[0] == (
        "field_distress_signal"
    )
    assert result["cash_need_score_missing_optional_indicators"].iloc[0] == (
        "livelihood_loss_proxy"
    )
    assert result["cash_feasibility_score_missing_optional_indicators"].iloc[0] == (
        "delivery_feasibility"
    )
    assert result["road_repair_priority_missing_optional_indicators"].iloc[0] == (
        "aid_route_importance,repair_difficulty"
    )
    assert result["cash_need_score_model_completeness_flag"].iloc[0] == (
        "optional_missing"
    )
    assert result["cash_priority_missing_optional_indicators"].iloc[0] == (
        "livelihood_loss_proxy,delivery_feasibility"
    )
    assert result["cash_priority_data_quality_flag"].iloc[0] == "medium"
    assert result["cash_priority_model_completeness_flag"].iloc[0] == (
        "optional_missing"
    )


def test_optional_missing_values_renormalize_available_weights():
    df = pd.DataFrame({"required_need": [0, 5, 10], "optional_need": [0, None, 10]})

    result = compute_weighted_score(
        df,
        weights={"required_need": 0.5, "optional_need": 0.5},
        score_name="review_score",
        missing_policy="skip",
        required_indicators=["required_need"],
        optional_indicators=["optional_need"],
    )

    assert result["review_score"].tolist() == [0.0, 0.5, 1.0]
    assert result.loc[1, "review_score_missing_optional_indicators"] == (
        "optional_need"
    )
    assert result.loc[1, "review_score_row_weight_sum_used"] == 0.5


def test_config_driven_computation_using_baseline_flood_config():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe()

    result = compute_priority_scores(df, config)

    expected_scores = [
        "need_severity",
        "lifeline_disruption",
        "rescue_priority",
        "cash_need_score",
        "cash_feasibility_score",
        "cash_priority",
        "health_support_priority",
        "road_repair_priority",
    ]
    for score in expected_scores:
        assert score in result.columns
        assert result[score].notna().all()
    assert "need_severity_component_exposed_population" in result.columns
    assert "road_repair_priority_cost_index" in result.columns


def test_cash_priority_keeps_need_and_feasibility_separate():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe()

    result = compute_priority_scores(df, config)

    assert result["cash_priority"].equals(result["cash_need_score"])
    assert result["cash_priority_feasibility_component"].equals(
        result["cash_feasibility_score"]
    )
    assert "Feasibility is not humanitarian need" in result[
        "cash_priority_warning"
    ].iloc[0]


def test_cash_priority_propagates_missing_feasibility_completeness():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe().drop(columns=["delivery_feasibility"])

    result = compute_priority_scores(df, config)

    assert result["cash_priority"].equals(result["cash_need_score"])
    assert result["cash_priority_missing_optional_indicators"].iloc[0] == (
        "delivery_feasibility"
    )
    assert result["cash_priority_data_quality_flag"].iloc[0] == "medium"
    assert result["cash_priority_model_completeness_flag"].iloc[0] == (
        "optional_missing"
    )


def test_road_repair_missing_optional_repair_difficulty_is_flagged():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe().drop(columns=["repair_difficulty"])

    result = compute_priority_scores(df, config)

    assert result["road_repair_priority"].notna().all()
    assert result["road_repair_priority_missing_optional_indicators"].iloc[0] == (
        "repair_difficulty"
    )
    assert result["road_repair_priority_model_completeness_flag"].iloc[0] == (
        "optional_missing"
    )


def test_road_repair_missing_required_segment_length_column_raises():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe().drop(columns=["segment_length_km"])

    with pytest.raises(MissingIndicatorError, match="segment_length_km"):
        compute_priority_scores(df, config)


def test_benefit_over_cost_with_zero_or_equal_costs_is_safe():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe()
    df["repair_difficulty"] = 0
    df["segment_length_km"] = 0

    result = compute_priority_scores(df, config)

    assert result["road_repair_priority_cost_index"].tolist() == [0.0, 0.0, 0.0]
    assert result["road_repair_priority"].equals(
        result["road_repair_priority_benefit_index"]
    )
    assert result["road_repair_priority"].notna().all()


def test_road_repair_epsilon_must_be_positive():
    config = load_priority_config(CONFIG_PATH)
    config = deepcopy(config)
    config["scores"]["road_repair_priority"]["epsilon"] = 0
    df = _complete_priority_dataframe()

    with pytest.raises(ValueError, match="epsilon"):
        compute_priority_scores(df, config)


def test_road_repair_missing_aid_route_importance_renormalizes_benefit():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe().drop(columns=["aid_route_importance"])

    result = compute_priority_scores(df, config)

    assert result["road_repair_priority_benefit_row_weight_sum_used"].tolist() == [
        0.8,
        0.8,
        0.8,
    ]
    assert result["road_repair_priority_benefit_index"].notna().all()
    assert result["road_repair_priority_missing_optional_indicators"].iloc[0] == (
        "aid_route_importance"
    )


def test_road_repair_required_cost_value_missing_does_not_create_high_priority():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe()
    df.loc[2, "segment_length_km"] = None

    result = compute_priority_scores(df, config)

    assert pd.isna(result.loc[2, "road_repair_priority"])
    assert result.loc[2, "road_repair_priority_missing_required_indicators"] == (
        "segment_length_km"
    )
    assert result.loc[2, "road_repair_priority_data_quality_flag"] == "low"


def test_score_entity_metadata_is_reported():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe()

    result = compute_priority_scores(df, config)

    assert result["need_severity_entity"].unique().tolist() == ["admin_area"]
    assert result["road_repair_priority_entity"].unique().tolist() == ["road_segment"]


def test_data_quality_flags_and_model_completeness_flags_are_separate():
    df = pd.DataFrame(
        {
            "hazard": [1.0, None, None],
            "exposure": [2.0, 3.0, None],
            "field_report": [1.0, None, None],
        }
    )

    result = assign_data_quality_flags(
        df,
        required_indicators=["hazard", "exposure"],
        optional_indicators=["field_report", "local_validation"],
    )

    assert result["data_quality_flag"].tolist() == [
        "medium",
        "low",
        "insufficient",
    ]
    assert result["model_completeness_flag"].tolist() == [
        "optional_missing",
        "required_missing",
        "insufficient",
    ]
    assert result["missing_optional_indicators"].iloc[0] == "local_validation"
    assert result["missing_required_indicators"].iloc[1] == "hazard"


def _complete_priority_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "area_id": ["a", "b", "c"],
            "hazard_severity": [0.2, 0.5, 0.9],
            "exposed_population": [100, 250, 500],
            "vulnerability": [0.1, 0.5, 0.8],
            "lack_of_coping_capacity": [0.2, 0.6, 0.9],
            "health_facility_disruption": [0, 1, 3],
            "transport_disruption": [1, 2, 4],
            "shelter_school_disruption": [0, 2, 2],
            "energy_disruption": [0, 1, 1],
            "isolation": [0, 0.5, 1],
            "time_criticality": [0.2, 0.8, 1.0],
            "field_distress_signal": [0, 1, 2],
            "exposed_households": [20, 60, 120],
            "livelihood_loss_proxy": [0.0, 0.4, 0.9],
            "delivery_feasibility": [1.0, 0.6, 0.2],
            "alternative_health_access_loss": [0.0, 0.5, 1.0],
            "vulnerable_population": [10, 50, 100],
            "population_reconnected": [100, 300, 600],
            "health_facilities_reconnected": [0, 1, 2],
            "shelters_schools_reconnected": [1, 1, 3],
            "aid_route_importance": [0.2, 0.6, 1.0],
            "repair_difficulty": [0.2, 0.5, 1.0],
            "segment_length_km": [1.0, 2.0, 4.0],
        }
    )
