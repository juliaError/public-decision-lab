"""Adapter interfaces and local-file adapters."""

from disaster_nowcaster.adapters.base import (
    AdapterMetadata,
    AdapterResult,
    EventAdapter,
    HazardAdapter,
    InfrastructureAdapter,
    PopulationAdapter,
)
from disaster_nowcaster.adapters.copernicus_gfm import LocalCopernicusGFMFloodAdapter
from disaster_nowcaster.adapters.gdacs import LocalGdacsEventAdapter
from disaster_nowcaster.adapters.local_hazard import LocalHazardAdapter
from disaster_nowcaster.adapters.nasa_lance import LocalNasaLanceFloodAdapter

__all__ = [
    "AdapterMetadata",
    "AdapterResult",
    "EventAdapter",
    "HazardAdapter",
    "InfrastructureAdapter",
    "PopulationAdapter",
    "LocalCopernicusGFMFloodAdapter",
    "LocalGdacsEventAdapter",
    "LocalHazardAdapter",
    "LocalNasaLanceFloodAdapter",
]
