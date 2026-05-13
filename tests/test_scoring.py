from pathlib import Path

import pandas as pd
import pytest

from disaster_nowcaster.scoring import (
    MissingIndicatorError,
    assign_data_quality_flags,
    compute_priority_scores,
    compute_weighted_score,
    load_priority_config,
    min_max_normalize,
    normalize_indicators,
)


CONFIG_PATH = Path("configs/priority_models/baseline_flood.yml")


def test_min_max_normalization_scales_to_unit_interval():
    values = pd.Series([0, 5, 10])

    normalized = min_max_normalize(values)

    assert normalized.tolist() == [0.0, 0.5, 1.0]


def test_equal_value_normalization_returns_neutral_zero():
    values = pd.Series([3, 3, 3])

    normalized = min_max_normalize(values)

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


def test_missing_required_indicators_raise_explicit_error():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe().drop(columns=["hazard_severity"])

    with pytest.raises(MissingIndicatorError, match="hazard_severity"):
        compute_priority_scores(df, config)


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
    assert result["cash_priority_missing_optional_indicators"].iloc[0] == (
        "livelihood_loss_proxy,delivery_feasibility"
    )
    assert result["road_repair_priority_missing_optional_indicators"].iloc[0] == (
        "repair_difficulty,aid_route_importance"
    )
    assert result["cash_priority_data_quality_flag"].iloc[0] == "medium"


def test_config_driven_computation_using_baseline_flood_config():
    config = load_priority_config(CONFIG_PATH)
    df = _complete_priority_dataframe()

    result = compute_priority_scores(df, config)

    expected_scores = [
        "need_severity",
        "lifeline_disruption",
        "rescue_priority",
        "cash_priority",
        "health_support_priority",
        "road_repair_priority",
    ]
    for score in expected_scores:
        assert score in result.columns
        assert result[score].notna().all()
    assert "need_severity_component_exposed_population" in result.columns
    assert "road_repair_priority_cost_index" in result.columns


def test_data_quality_flags_reflect_missing_required_and_optional_values():
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
