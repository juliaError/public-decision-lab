"""Infrastructure layer loading helpers."""

from __future__ import annotations

from pathlib import Path

from disaster_nowcaster.geojson_io import load_vector_layer
from disaster_nowcaster.schemas import Feature, GeoJSONLayer

SUPPORTED_ROAD_TYPES = {"LineString", "MultiLineString"}
SUPPORTED_FACILITY_GEOMETRY_TYPES = {"Point", "MultiPoint", "Polygon", "MultiPolygon"}
SUPPORTED_FACILITY_TYPES = {"hospital", "clinic", "school", "shelter"}

FACILITY_TAG_ALIASES = {
    "doctors": "clinic",
    "healthcare": "clinic",
    "yes": "",
}


def load_infrastructure(path: str | Path, name: str) -> GeoJSONLayer:
    """Load road or facility infrastructure features from GeoJSON or GeoPackage."""

    layer = load_vector_layer(path, name=name)
    for index, feature in enumerate(layer.features):
        geometry_type = feature["geometry"].get("type")
        if name == "roads" and geometry_type not in SUPPORTED_ROAD_TYPES:
            raise ValueError(f"{layer.path} road feature {index} must be a line geometry.")
        if name == "facilities" and geometry_type not in SUPPORTED_FACILITY_GEOMETRY_TYPES:
            raise ValueError(
                f"{layer.path} facility feature {index} must be a point or polygon geometry."
            )
    if name == "facilities":
        return GeoJSONLayer(
            name=layer.name,
            path=layer.path,
            features=_supported_facility_features(layer.features),
        )
    return layer


def normalize_facility_type(feature: Feature) -> str | None:
    """Return a supported facility type from common OSM/HOT tags."""

    properties = feature.get("properties", {})
    candidates = [
        properties.get("facility_type"),
        properties.get("amenity"),
        properties.get("healthcare"),
        properties.get("building"),
    ]
    for value in candidates:
        if value is None:
            continue
        raw_value = str(value).strip().lower()
        normalized = FACILITY_TAG_ALIASES.get(raw_value, raw_value)
        if normalized in SUPPORTED_FACILITY_TYPES:
            return normalized
    return None


def _supported_facility_features(features: list[Feature]) -> list[Feature]:
    supported: list[Feature] = []
    for feature in features:
        facility_type = normalize_facility_type(feature)
        if not facility_type:
            continue
        copied = {
            "type": feature["type"],
            "geometry": feature["geometry"],
            "properties": dict(feature.get("properties", {})),
        }
        copied["properties"]["facility_type"] = facility_type
        supported.append(copied)
    return supported
