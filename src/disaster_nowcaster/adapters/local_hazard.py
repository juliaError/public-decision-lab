"""Local-file hazard adapter."""

from __future__ import annotations

from pathlib import Path

from disaster_nowcaster.adapters.base import AdapterMetadata, AdapterResult
from disaster_nowcaster.events import DisasterEvent
from disaster_nowcaster.hazard import load_hazard


class LocalHazardAdapter:
    """Wrap an existing local hazard GeoJSON as a standardized adapter result."""

    def __init__(
        self,
        path: str | Path,
        *,
        source_name: str = "Local user-supplied hazard layer",
        hazard_type: str = "unknown",
        source_url: str | None = None,
        license_or_terms: str | None = None,
        notes: list[str] | None = None,
    ) -> None:
        self.path = Path(path)
        self.hazard_type = hazard_type
        self.metadata = AdapterMetadata(
            source_name=source_name,
            source_url=source_url,
            license_or_terms=license_or_terms,
            source_type="manual",
            observed_or_modeled="user_supplied",
            known_limitations=[
                "Local hazard input is not validated by this adapter.",
                "Exposure screening does not confirm damage.",
                "CRS and timing must be checked before operational use.",
            ],
            auto_downloaded=False,
            notes=notes or [],
        )

    def prepare(self, event: DisasterEvent | None = None) -> AdapterResult:
        """Validate the local hazard file and return its path with metadata."""

        if event and event.hazard_type != self.hazard_type and self.hazard_type != "unknown":
            raise ValueError(
                f"Event hazard type {event.hazard_type!r} does not match adapter "
                f"hazard type {self.hazard_type!r}."
            )
        load_hazard(self.path)
        return AdapterResult(
            path=self.path,
            layer_name="hazard",
            metadata=self.metadata,
        )
