"""Disaster Impact Nowcaster package."""

from disaster_nowcaster.exposure import compute_exposure
from disaster_nowcaster.population import compute_population_exposure
from disaster_nowcaster.schemas import ExposureResult, GeoJSONLayer, RunConfig

__all__ = [
    "ExposureResult",
    "GeoJSONLayer",
    "RunConfig",
    "compute_exposure",
    "compute_population_exposure",
]

__version__ = "0.1.0"
