from pathlib import Path

from disaster_nowcaster.admin import load_admin_units
from disaster_nowcaster.aoi import load_aoi
from disaster_nowcaster.exposure import compute_exposure
from disaster_nowcaster.hazard import load_hazard
from disaster_nowcaster.infrastructure import load_infrastructure


FIXTURES = Path(__file__).parent / "fixtures"


def test_compute_exposure_counts_synthetic_features():
    aoi = load_aoi(FIXTURES / "aoi.geojson")
    hazard = load_hazard(FIXTURES / "hazard.geojson")
    roads = load_infrastructure(FIXTURES / "roads.geojson", name="roads")
    facilities = load_infrastructure(FIXTURES / "facilities.geojson", name="facilities")
    admin = load_admin_units(FIXTURES / "admin.geojson")

    result = compute_exposure(
        aoi=aoi,
        hazard=hazard,
        roads=roads,
        facilities=facilities,
        admin=admin,
    )

    assert result.hazard_intersects_aoi is True
    assert result.admin_feature_count == 2
    assert result.road_feature_count == 2
    assert result.facility_feature_count == 2
    assert result.affected_road_count == 1
    assert result.affected_facility_count == 1
    assert result.affected_roads[0]["properties"]["id"] == "affected_road"
    assert result.affected_facilities[0]["properties"]["id"] == "affected_facility"
    assert result.priority_areas[0]["demo_priority_score"] == 2
    assert result.priority_areas[0]["admin_name"] == "Synthetic East District"
