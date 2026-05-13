"""Case-study manifest validation and scaffolding utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CASE_INPUT_KEYS = ("aoi", "hazard", "admin", "population", "roads", "facilities")
CASE_STAGE_IDS = ("T0_baseline", "T1_early_hazard", "T2_updated_hazard", "T3_diagnostic")
CASE_STATUSES = (
    "candidate",
    "source_review",
    "data_gap",
    "data_ready",
    "run_complete",
    "evaluated",
    "iteration_needed",
    "report_ready",
)
SOURCE_ROLES = ("input", "validation", "narrative", "response_timeline", "context")

CASE_DOC_TEMPLATES = {
    "case_note.md": """# {case_id} Case Note

## Case Summary

TODO: Summarize the event using traceable sources. Distinguish event-time knowledge from post-event evidence.

## Evaluation Purpose

TODO: Explain what this case tests for Disaster Impact Nowcaster.

## Data Availability

TODO: Record available AOI, hazard, admin, population, roads, and facilities inputs. Mark data gaps explicitly.

## Non-Claims

- Exposure outputs are not confirmed damage.
- Priority outputs are not official allocation rules.
- Any proxy hazard input must be labeled as a proxy, not as observed inundation.
""",
    "sources.md": """# {case_id} Sources

| Source ID | Title | Publisher | URL/path | Access date | Availability | Role | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | during_event / post_event | input / validation / narrative / response_timeline / context |  |
""",
    "run_log.md": """# {case_id} Run Log

## Run Stages

| Stage | Data cut-off | Status | Output path | Notes |
| --- | --- | --- | --- | --- |
| T0_baseline |  | planned |  |  |
| T1_early_hazard |  | planned |  |  |
| T2_updated_hazard |  | planned |  |  |
| T3_diagnostic |  | planned |  |  |

## Commands

```bash
disaster-nowcaster run \\
  --aoi <path> \\
  --hazard <path> \\
  --roads <path> \\
  --facilities <path> \\
  --admin <path> \\
  --population <path> \\
  --output outputs/<case_id>/<run_id>
```
""",
    "evaluation.md": """# {case_id} Evaluation

## Exposure Summary Usefulness

TODO: Compare outputs with traceable public evidence.

## Priority Ranking Review

TODO: Assess whether top-k areas would have supported useful review.

## Infrastructure And Access

TODO: Review roads, facilities, shelters, hospitals, and access constraints.

## Timeliness

TODO: Assess whether the system could have run before or during response-relevant decisions.

## Failure Modes

TODO: Record missing data, weak assumptions, misleading outputs, and upgrade needs.

## Usefulness Judgment

Status: insufficient_evidence
""",
}


class CaseManifestError(ValueError):
    """Raised when a case-study manifest is incomplete or invalid."""


def load_case_manifest(path: str | Path) -> dict[str, Any]:
    """Load and validate a single case-study YAML manifest."""

    manifest_path = Path(path)
    with manifest_path.open("r", encoding="utf-8") as file:
        payload = yaml.safe_load(file)
    return validate_case_manifest(payload, source=str(manifest_path))


def validate_case_manifest(payload: Any, *, source: str = "manifest") -> dict[str, Any]:
    """Validate a case-study manifest and return the normalized payload."""

    if not isinstance(payload, dict) or not isinstance(payload.get("case"), dict):
        raise CaseManifestError(f"{source} must contain a top-level case object.")
    case = payload["case"]
    _require_keys(
        case,
        (
            "case_id",
            "event_name",
            "hazard_type",
            "country_or_region",
            "event_period",
            "status",
            "source_inventory",
            "run_stages",
        ),
        f"{source}.case",
    )
    if case["status"] not in CASE_STATUSES:
        raise CaseManifestError(
            f"{source}.case.status must be one of {', '.join(CASE_STATUSES)}."
        )
    _validate_source_inventory(case["source_inventory"], source)
    _validate_run_stages(case["run_stages"], source)
    return payload


def scaffold_case_directory(
    case_id: str,
    output_dir: str | Path,
    *,
    overwrite: bool = False,
) -> list[Path]:
    """Create standard case-study documentation files."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, template in CASE_DOC_TEMPLATES.items():
        path = output_path / filename
        if path.exists() and not overwrite:
            raise FileExistsError(f"{path} already exists. Use overwrite=True to replace it.")
        path.write_text(template.format(case_id=case_id), encoding="utf-8")
        written.append(path)
    return written


def _validate_source_inventory(value: Any, source: str) -> None:
    if not isinstance(value, list) or not value:
        raise CaseManifestError(f"{source}.case.source_inventory must be a non-empty list.")
    for index, item in enumerate(value):
        location = f"{source}.case.source_inventory[{index}]"
        if not isinstance(item, dict):
            raise CaseManifestError(f"{location} must be an object.")
        _require_keys(
            item,
            (
                "source_id",
                "title",
                "publisher",
                "url_or_path",
                "access_date",
                "availability",
                "role",
                "notes",
            ),
            location,
        )
        if item["role"] not in SOURCE_ROLES:
            raise CaseManifestError(
                f"{location}.role must be one of {', '.join(SOURCE_ROLES)}."
            )
        if item["availability"] not in {"during_event", "post_event", "unknown"}:
            raise CaseManifestError(
                f"{location}.availability must be during_event, post_event, or unknown."
            )


def _validate_run_stages(value: Any, source: str) -> None:
    if not isinstance(value, list) or not value:
        raise CaseManifestError(f"{source}.case.run_stages must be a non-empty list.")
    seen_stages: set[str] = set()
    for index, item in enumerate(value):
        location = f"{source}.case.run_stages[{index}]"
        if not isinstance(item, dict):
            raise CaseManifestError(f"{location} must be an object.")
        _require_keys(
            item,
            ("stage", "data_cutoff", "stage_status", "input_paths", "uncertainty_notes"),
            location,
        )
        if item["stage"] not in CASE_STAGE_IDS:
            raise CaseManifestError(
                f"{location}.stage must be one of {', '.join(CASE_STAGE_IDS)}."
            )
        seen_stages.add(item["stage"])
        if not isinstance(item["input_paths"], dict):
            raise CaseManifestError(f"{location}.input_paths must be an object.")
        missing_inputs = [key for key in CASE_INPUT_KEYS if key not in item["input_paths"]]
        if missing_inputs:
            raise CaseManifestError(
                f"{location}.input_paths is missing: {', '.join(missing_inputs)}."
            )
        if not isinstance(item["uncertainty_notes"], list) or not item["uncertainty_notes"]:
            raise CaseManifestError(f"{location}.uncertainty_notes must be non-empty.")
    missing_stages = [stage for stage in CASE_STAGE_IDS if stage not in seen_stages]
    if missing_stages:
        raise CaseManifestError(
            f"{source}.case.run_stages is missing: {', '.join(missing_stages)}."
        )


def _require_keys(mapping: dict[str, Any], keys: tuple[str, ...], location: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise CaseManifestError(f"{location} is missing required keys: {', '.join(missing)}.")
