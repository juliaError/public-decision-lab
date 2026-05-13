from pathlib import Path

import pytest

from disaster_nowcaster.adapters import AdapterMetadata, LocalHazardAdapter
from disaster_nowcaster.events import DisasterEvent


FIXTURES = Path(__file__).parent / "fixtures"


def test_adapter_metadata_is_serializable_and_cautious():
    metadata = AdapterMetadata(
        source_name="Synthetic local source",
        source_type="manual",
        observed_or_modeled="user_supplied",
        known_limitations=["Exposure screening does not confirm damage."],
        auto_downloaded=False,
    )

    payload = metadata.to_dict()

    assert payload["source_name"] == "Synthetic local source"
    assert payload["auto_downloaded"] is False
    assert "does not confirm damage" in payload["known_limitations"][0]


def test_local_hazard_adapter_returns_local_path_and_metadata():
    adapter = LocalHazardAdapter(
        FIXTURES / "hazard.geojson",
        source_name="Synthetic hazard fixture",
        hazard_type="flood",
    )

    result = adapter.prepare()

    assert result.path == FIXTURES / "hazard.geojson"
    assert result.layer_name == "hazard"
    assert result.metadata.source_name == "Synthetic hazard fixture"
    assert result.metadata.auto_downloaded is False
    assert result.metadata.source_type == "manual"
    assert any("not validated" in item for item in result.metadata.known_limitations)


def test_local_hazard_adapter_checks_event_hazard_type():
    adapter = LocalHazardAdapter(FIXTURES / "hazard.geojson", hazard_type="flood")
    event = DisasterEvent(
        event_id="synthetic-earthquake",
        hazard_type="earthquake",
        name="Synthetic earthquake",
        source="unit_test",
    )

    with pytest.raises(ValueError, match="does not match"):
        adapter.prepare(event)


def test_local_hazard_adapter_accepts_matching_event():
    adapter = LocalHazardAdapter(FIXTURES / "hazard.geojson", hazard_type="flood")
    event = DisasterEvent(
        event_id="synthetic-flood",
        hazard_type="flood",
        name="Synthetic flood",
        source="unit_test",
    )

    result = adapter.prepare(event)

    assert result.path.name == "hazard.geojson"
