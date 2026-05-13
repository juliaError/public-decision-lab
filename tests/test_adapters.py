from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from disaster_nowcaster.adapters import (
    AdapterMetadata,
    LocalHazardAdapter,
    LocalNasaLanceFloodAdapter,
)
from disaster_nowcaster.events import DisasterEvent
from disaster_nowcaster.hazard import load_hazard


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


def test_local_nasa_lance_flood_adapter_writes_hazard_geojson(tmp_path):
    raster_path = tmp_path / "synthetic_lance_flood.tif"
    output_path = tmp_path / "hazard_from_lance.geojson"
    _write_synthetic_flood_raster(raster_path)
    adapter = LocalNasaLanceFloodAdapter(
        raster_path,
        output_path,
        flood_value=1,
        notes=["Synthetic fixture only."],
    )

    result = adapter.prepare(
        DisasterEvent(
            event_id="synthetic-flood",
            hazard_type="flood",
            name="Synthetic flood",
            source="unit_test",
        )
    )
    hazard_layer = load_hazard(result.path)

    assert result.path == output_path
    assert result.layer_name == "hazard"
    assert result.metadata.auto_downloaded is False
    assert "does not download NASA LANCE data" in result.metadata.known_limitations[0]
    assert len(hazard_layer.features) >= 1
    assert hazard_layer.features[0]["properties"]["threshold"] == 1.0


def test_local_nasa_lance_flood_adapter_rejects_non_flood_event(tmp_path):
    raster_path = tmp_path / "synthetic_lance_flood.tif"
    output_path = tmp_path / "hazard_from_lance.geojson"
    _write_synthetic_flood_raster(raster_path)
    adapter = LocalNasaLanceFloodAdapter(raster_path, output_path)

    with pytest.raises(ValueError, match="requires flood event"):
        adapter.prepare(
            DisasterEvent(
                event_id="synthetic-fire",
                hazard_type="wildfire",
                name="Synthetic wildfire",
                source="unit_test",
            )
        )


def _write_synthetic_flood_raster(path: Path) -> None:
    data = np.array(
        [
            [0, 1, 1],
            [0, 0, 1],
            [0, 0, 0],
        ],
        dtype="uint8",
    )
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype="uint8",
        transform=from_origin(0, 3, 1, 1),
        nodata=255,
    ) as dataset:
        dataset.write(data, 1)
