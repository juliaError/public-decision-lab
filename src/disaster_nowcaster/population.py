"""Local population raster exposure calculations."""

from __future__ import annotations

from math import isfinite
from pathlib import Path

import numpy as np
import rasterio
from rasterio.features import geometry_mask

from disaster_nowcaster.schemas import GeoJSONLayer, PopulationExposureResult, PriorityRow


def compute_population_exposure(
    population_raster: str | Path,
    hazard: GeoJSONLayer,
    admin: GeoJSONLayer,
) -> PopulationExposureResult:
    """Estimate exposed population from a local GeoTIFF.

    Raster cell values are treated as estimated people per cell. The raster and
    GeoJSON layers must already share the same coordinate reference system.
    """

    raster_path = Path(population_raster)
    with rasterio.open(raster_path) as dataset:
        population = dataset.read(1, masked=True).astype("float64")
        hazard_mask = geometry_mask(
            [feature["geometry"] for feature in hazard.features],
            out_shape=population.shape,
            transform=dataset.transform,
            invert=True,
            all_touched=False,
        )
        values = _valid_population_values(population, hazard_mask)
        total = float(values.sum())
        cell_count = int(values.size)

        admin_rows: list[PriorityRow] = []
        for index, feature in enumerate(admin.features, start=1):
            admin_mask = geometry_mask(
                [feature["geometry"]],
                out_shape=population.shape,
                transform=dataset.transform,
                invert=True,
                all_touched=False,
            )
            admin_values = _valid_population_values(population, hazard_mask & admin_mask)
            properties = feature.get("properties", {})
            admin_rows.append(
                {
                    "admin_id": properties.get("id", f"admin_{index}"),
                    "admin_name": properties.get("name", f"Admin unit {index}"),
                    "estimated_exposed_population": float(admin_values.sum()),
                    "population_cell_count": int(admin_values.size),
                }
            )

    return PopulationExposureResult(
        raster_path=raster_path,
        estimated_exposed_population=total,
        exposed_population_by_admin=admin_rows,
        included_cell_count=cell_count,
    )


def _valid_population_values(population, include_mask):
    filled = np.ma.filled(population, np.nan)
    valid = include_mask & np.isfinite(filled) & (filled >= 0)
    return filled[valid]
