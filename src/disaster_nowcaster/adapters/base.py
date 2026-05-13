"""Base contracts for replaceable data-source adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from disaster_nowcaster.events import DisasterEvent


@dataclass(frozen=True)
class AdapterMetadata:
    """Document provenance and limitations for one adapter output."""

    source_name: str
    source_url: str | None = None
    license_or_terms: str | None = None
    spatial_resolution: str | None = None
    temporal_resolution: str | None = None
    update_frequency: str | None = None
    source_type: str = "manual"
    observed_or_modeled: str | None = None
    known_limitations: list[str] = field(default_factory=list)
    auto_downloaded: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Return JSON-serializable metadata."""

        return {
            "source_name": self.source_name,
            "source_url": self.source_url,
            "license_or_terms": self.license_or_terms,
            "spatial_resolution": self.spatial_resolution,
            "temporal_resolution": self.temporal_resolution,
            "update_frequency": self.update_frequency,
            "source_type": self.source_type,
            "observed_or_modeled": self.observed_or_modeled,
            "known_limitations": self.known_limitations,
            "auto_downloaded": self.auto_downloaded,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class AdapterResult:
    """A standardized local artifact produced by an adapter."""

    path: Path
    layer_name: str
    metadata: AdapterMetadata


class HazardAdapter(Protocol):
    """Protocol for adapters that prepare local hazard inputs."""

    metadata: AdapterMetadata

    def prepare(self, event: DisasterEvent | None = None) -> AdapterResult:
        """Prepare a local hazard artifact for the core pipeline."""


class PopulationAdapter(Protocol):
    """Protocol for adapters that prepare local population inputs."""

    metadata: AdapterMetadata

    def prepare(self, event: DisasterEvent | None = None) -> AdapterResult:
        """Prepare a local population artifact for the core pipeline."""


class InfrastructureAdapter(Protocol):
    """Protocol for adapters that prepare roads, facilities, or other assets."""

    metadata: AdapterMetadata

    def prepare(self, event: DisasterEvent | None = None) -> AdapterResult:
        """Prepare a local infrastructure artifact for the core pipeline."""


class EventAdapter(Protocol):
    """Protocol for adapters that discover or normalize disaster events."""

    metadata: AdapterMetadata

    def list_events(self) -> list[DisasterEvent]:
        """Return event metadata without running the exposure pipeline."""
