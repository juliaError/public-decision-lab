"""Shared helpers for local raster-to-hazard adapter outputs."""

from __future__ import annotations

from pathlib import Path

import rasterio
from rasterio.features import shapes

from disaster_nowcaster.geojson_io import write_feature_collection
from disaster_nowcaster.schemas import Feature


def polygonize_thresholded_raster(
    raster_path: str | Path,
    *,
    threshold: float,
    source: str,
    value_property: str,
    extra_properties: dict[str, object] | None = None,
) -> list[Feature]:
    """Return polygons for raster cells with values at or above a threshold.

    The helper is intentionally simple for v0.1 local adapters. It does not
    reproject, resample, validate product class semantics, or infer scientific
    meaning from raster values. Callers must document those assumptions.
    """

    properties = extra_properties or {}
    features: list[Feature] = []
    with rasterio.open(raster_path) as dataset:
        band = dataset.read(1)
        valid_mask = band >= threshold
        if dataset.nodata is not None:
            valid_mask = valid_mask & (band != dataset.nodata)

        for geometry, value in shapes(
            band.astype("float32"),
            mask=valid_mask,
            transform=dataset.transform,
        ):
            if float(value) < threshold:
                continue
            features.append(
                {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "source": source,
                        value_property: float(value),
                        "threshold": float(threshold),
                        **properties,
                    },
                }
            )
    return features


def write_thresholded_raster_hazard_geojson(
    raster_path: str | Path,
    output_geojson: str | Path,
    *,
    threshold: float,
    source: str,
    value_property: str,
    extra_properties: dict[str, object] | None = None,
) -> list[Feature]:
    """Polygonize thresholded raster cells and write a hazard GeoJSON file."""

    features = polygonize_thresholded_raster(
        raster_path,
        threshold=threshold,
        source=source,
        value_property=value_property,
        extra_properties=extra_properties,
    )
    write_feature_collection(output_geojson, features)
    return features
