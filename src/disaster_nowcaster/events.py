"""Event metadata structures for adapter-driven nowcasting."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DisasterEvent:
    """Minimal event metadata shared by adapters and the local pipeline."""

    event_id: str
    hazard_type: str
    name: str
    source: str
    start_time_utc: str | None = None
    end_time_utc: str | None = None
    description: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EventWindow:
    """Optional temporal window for event-specific data queries."""

    start_time_utc: str | None = None
    end_time_utc: str | None = None
