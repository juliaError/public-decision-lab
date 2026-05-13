"""Hazard layer loading helpers."""

from __future__ import annotations

from pathlib import Path

from disaster_nowcaster.geojson_io import load_geojson_layer
from disaster_nowcaster.geometry import extract_polygons
from disaster_nowcaster.schemas import GeoJSONLayer


def load_hazard(path: str | Path) -> GeoJSONLayer:
    """Load a hazard polygon layer from GeoJSON."""

    layer = load_geojson_layer(path, name="hazard")
    for feature in layer.features:
        extract_polygons(feature["geometry"])
    return layer
