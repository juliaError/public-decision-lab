"""Core data structures for the minimal nowcaster skeleton."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

Feature = dict[str, Any]
PriorityRow = dict[str, Any]


@dataclass(frozen=True)
class GeoJSONLayer:
    """A loaded GeoJSON feature layer."""

    name: str
    path: Path
    features: list[Feature]


@dataclass(frozen=True)
class RunConfig:
    """Input and output paths for one nowcaster run."""

    aoi: Path
    hazard: Path
    roads: Path
    facilities: Path
    admin: Path
    population: Path | None
    output: Path
    overwrite: bool = False


@dataclass(frozen=True)
class PopulationExposureResult:
    """Estimated population exposure from a local raster."""

    raster_path: Path
    estimated_exposed_population: float
    exposed_population_by_admin: list[PriorityRow]
    included_cell_count: int


@dataclass(frozen=True)
class ExposureResult:
    """Simple exposure counts from intersection-based screening."""

    aoi_feature_count: int
    hazard_feature_count: int
    admin_feature_count: int
    road_feature_count: int
    facility_feature_count: int
    affected_road_count: int
    affected_road_length: float
    affected_facility_count: int
    affected_facilities_by_type: PriorityRow
    affected_facilities_by_admin: list[PriorityRow]
    affected_roads: list[Feature]
    affected_facilities: list[Feature]
    priority_areas: list[PriorityRow]
    hazard_intersects_aoi: bool
    population_exposure: PopulationExposureResult | None = None
