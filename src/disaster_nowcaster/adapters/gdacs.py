"""Local GDACS-style event manifest adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from disaster_nowcaster.adapters.base import AdapterMetadata
from disaster_nowcaster.events import DisasterEvent


class LocalGdacsEventAdapter:
    """Read local GDACS-style event metadata from JSON.

    The adapter is deliberately local-only. It normalizes event metadata for
    future orchestration tests without polling GDACS or triggering pipelines.
    """

    def __init__(
        self,
        manifest_path: str | Path,
        *,
        source_name: str = "GDACS-style local event manifest",
        source_url: str | None = "https://www.gdacs.org/",
        license_or_terms: str | None = None,
        notes: list[str] | None = None,
    ) -> None:
        self.manifest_path = Path(manifest_path)
        self.metadata = AdapterMetadata(
            source_name=source_name,
            source_url=source_url,
            license_or_terms=license_or_terms,
            spatial_resolution="event metadata only; not a hazard layer",
            temporal_resolution="event metadata only; manifest-specific",
            update_frequency="not checked by local adapter",
            source_type="manual",
            observed_or_modeled="event_alert_metadata",
            known_limitations=[
                "This adapter only reads a local JSON manifest; it does not poll GDACS.",
                "Event alerts are triggers for review, not confirmed local damage.",
                "AOI, time window, and hazard products must be validated before running operational outputs.",
            ],
            auto_downloaded=False,
            notes=notes or [],
        )

    def list_events(self) -> list[DisasterEvent]:
        """Return events from a local manifest."""

        with self.manifest_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        records = self._event_records(payload)
        return [self._event_from_record(record, index) for index, record in enumerate(records)]

    @staticmethod
    def _event_records(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict) and isinstance(payload.get("events"), list):
            records = payload["events"]
        else:
            raise ValueError("GDACS-style manifest must be a list or contain an events list.")
        if not all(isinstance(record, dict) for record in records):
            raise ValueError("Every GDACS-style event record must be an object.")
        return records

    def _event_from_record(self, record: dict[str, Any], index: int) -> DisasterEvent:
        event_id = record.get("event_id") or record.get("id")
        hazard_type = record.get("hazard_type") or record.get("event_type")
        name = record.get("name") or record.get("title")
        if not event_id or not hazard_type or not name:
            raise ValueError(
                "GDACS-style event records require event_id/id, "
                f"hazard_type/event_type, and name/title; record {index} is incomplete."
            )
        metadata = record.get("metadata", {})
        if metadata is None:
            metadata = {}
        if not isinstance(metadata, dict):
            raise ValueError(f"GDACS-style event record {index} metadata must be an object.")
        return DisasterEvent(
            event_id=str(event_id),
            hazard_type=str(hazard_type),
            name=str(name),
            source=str(record.get("source") or self.metadata.source_name),
            start_time_utc=_optional_string(record.get("start_time_utc")),
            end_time_utc=_optional_string(record.get("end_time_utc")),
            description=_optional_string(record.get("description")),
            metadata={str(key): str(value) for key, value in metadata.items()},
        )


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
