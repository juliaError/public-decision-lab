"""Small GeoJSON readers and writers for local files."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from shapely.geometry import mapping
from shapely import wkb

from disaster_nowcaster.schemas import Feature, GeoJSONLayer

GPKG_ENVELOPE_LENGTHS = {
    0: 0,
    1: 32,
    2: 48,
    3: 48,
    4: 64,
}


def load_geojson_layer(path: str | Path, name: str | None = None) -> GeoJSONLayer:
    """Load a local GeoJSON FeatureCollection."""

    layer_path = Path(path)
    with layer_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if payload.get("type") != "FeatureCollection":
        raise ValueError(f"{layer_path} must be a GeoJSON FeatureCollection.")

    features = payload.get("features")
    if not isinstance(features, list):
        raise ValueError(f"{layer_path} must contain a list of features.")

    for index, feature in enumerate(features):
        if feature.get("type") != "Feature":
            raise ValueError(f"{layer_path} feature {index} is not a GeoJSON Feature.")
        if not isinstance(feature.get("geometry"), dict):
            raise ValueError(f"{layer_path} feature {index} is missing geometry.")

    return GeoJSONLayer(name=name or layer_path.stem, path=layer_path, features=features)


def load_vector_layer(path: str | Path, name: str | None = None) -> GeoJSONLayer:
    """Load a local GeoJSON or GeoPackage feature layer."""

    layer_path = Path(path)
    suffix = layer_path.suffix.lower()
    if suffix in {".geojson", ".json"}:
        return load_geojson_layer(layer_path, name=name)
    if suffix == ".gpkg":
        return _load_gpkg_layer(layer_path, name=name)
    raise ValueError(
        f"{layer_path} must be a GeoJSON (.geojson/.json) or GeoPackage (.gpkg) file."
    )


def write_feature_collection(path: str | Path, features: list[Feature]) -> None:
    """Write features as a GeoJSON FeatureCollection."""

    payload: dict[str, Any] = {
        "type": "FeatureCollection",
        "features": features,
    }
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)
        file.write("\n")


def _load_gpkg_layer(path: Path, name: str | None = None) -> GeoJSONLayer:
    with sqlite3.connect(path) as connection:
        table_name = _first_feature_table(connection)
        geometry_column = _geometry_column(connection, table_name)
        rows = connection.execute(f'SELECT * FROM "{table_name}"').fetchall()
        column_names = [
            item[1] for item in connection.execute(f'PRAGMA table_info("{table_name}")')
        ]

    features: list[Feature] = []
    for row in rows:
        record = dict(zip(column_names, row))
        geometry_blob = record.pop(geometry_column)
        geometry = _geometry_from_gpkg_blob(geometry_blob)
        properties = {key: value for key, value in record.items() if key.lower() != "fid"}
        features.append(
            {
                "type": "Feature",
                "properties": properties,
                "geometry": mapping(geometry),
            }
        )

    return GeoJSONLayer(name=name or table_name, path=path, features=features)


def _first_feature_table(connection: sqlite3.Connection) -> str:
    row = connection.execute(
        "SELECT table_name FROM gpkg_contents WHERE data_type = 'features' ORDER BY table_name LIMIT 1"
    ).fetchone()
    if not row:
        raise ValueError("GeoPackage does not contain a feature table.")
    return str(row[0])


def _geometry_column(connection: sqlite3.Connection, table_name: str) -> str:
    row = connection.execute(
        "SELECT column_name FROM gpkg_geometry_columns WHERE table_name = ? LIMIT 1",
        (table_name,),
    ).fetchone()
    if not row:
        raise ValueError(f"GeoPackage table {table_name!r} has no geometry column.")
    return str(row[0])


def _geometry_from_gpkg_blob(blob):
    data = bytes(blob)
    if data[:2] != b"GP":
        raise ValueError("GeoPackage geometry blob has an invalid magic header.")
    flags = data[3]
    envelope_code = (flags >> 1) & 0b111
    envelope_length = GPKG_ENVELOPE_LENGTHS.get(envelope_code)
    if envelope_length is None:
        raise ValueError(f"Unsupported GeoPackage envelope code: {envelope_code}.")
    wkb_offset = 8 + envelope_length
    return wkb.loads(data[wkb_offset:])
