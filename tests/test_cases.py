import pytest
import yaml

from disaster_nowcaster.cases import (
    CaseManifestError,
    load_case_manifest,
    scaffold_case_directory,
    validate_case_manifest,
)
from disaster_nowcaster.cli import main


def test_valid_case_manifest_passes():
    payload = _valid_case_manifest()

    result = validate_case_manifest(payload)

    assert result["case"]["case_id"] == "synthetic_case"


def test_case_manifest_requires_source_inventory():
    payload = _valid_case_manifest()
    payload["case"]["source_inventory"] = []

    with pytest.raises(CaseManifestError, match="source_inventory"):
        validate_case_manifest(payload)


def test_case_manifest_requires_all_run_stages():
    payload = _valid_case_manifest()
    payload["case"]["run_stages"] = payload["case"]["run_stages"][:1]

    with pytest.raises(CaseManifestError, match="T1_early_hazard"):
        validate_case_manifest(payload)


def test_case_manifest_requires_data_cutoff():
    payload = _valid_case_manifest()
    del payload["case"]["run_stages"][0]["data_cutoff"]

    with pytest.raises(CaseManifestError, match="data_cutoff"):
        validate_case_manifest(payload)


def test_case_manifest_rejects_invalid_status():
    payload = _valid_case_manifest()
    payload["case"]["status"] = "validated_truth"

    with pytest.raises(CaseManifestError, match="status"):
        validate_case_manifest(payload)


def test_case_manifest_requires_input_path_keys():
    payload = _valid_case_manifest()
    del payload["case"]["run_stages"][0]["input_paths"]["hazard"]

    with pytest.raises(CaseManifestError, match="hazard"):
        validate_case_manifest(payload)


def test_load_case_manifest_reads_yaml(tmp_path):
    manifest_path = tmp_path / "case.yml"
    manifest_path.write_text(yaml.safe_dump(_valid_case_manifest()), encoding="utf-8")

    result = load_case_manifest(manifest_path)

    assert result["case"]["status"] == "data_gap"


def test_scaffold_case_directory_creates_standard_files(tmp_path):
    output_dir = tmp_path / "case"

    written = scaffold_case_directory("synthetic_case", output_dir)

    assert sorted(path.name for path in written) == [
        "case_note.md",
        "evaluation.md",
        "run_log.md",
        "sources.md",
    ]
    assert "synthetic_case" in (output_dir / "case_note.md").read_text()


def test_cli_case_validate(tmp_path):
    manifest_path = tmp_path / "case.yml"
    manifest_path.write_text(yaml.safe_dump(_valid_case_manifest()), encoding="utf-8")

    exit_code = main(["case", "validate", "--manifest", str(manifest_path)])

    assert exit_code == 0


def test_cli_case_scaffold(tmp_path):
    output_dir = tmp_path / "case"

    exit_code = main(
        [
            "case",
            "scaffold",
            "--case-id",
            "synthetic_case",
            "--output",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    assert (output_dir / "sources.md").exists()


def _valid_case_manifest():
    input_paths = {
        "aoi": None,
        "hazard": None,
        "admin": None,
        "population": None,
        "roads": None,
        "facilities": None,
    }
    return {
        "case": {
            "case_id": "synthetic_case",
            "event_name": "Synthetic flood case",
            "hazard_type": "flood",
            "country_or_region": "Synthetic region",
            "event_period": "2026-01",
            "status": "data_gap",
            "source_inventory": [
                {
                    "source_id": "synthetic_source",
                    "title": "Synthetic source",
                    "publisher": "Unit tests",
                    "url_or_path": "local",
                    "access_date": "2026-05-14",
                    "availability": "post_event",
                    "role": "validation",
                    "notes": "Synthetic source only.",
                }
            ],
            "run_stages": [
                {
                    "stage": stage,
                    "data_cutoff": "2026-01-01T00:00:00Z",
                    "stage_status": "planned",
                    "input_paths": dict(input_paths),
                    "uncertainty_notes": ["Synthetic test note."],
                }
                for stage in (
                    "T0_baseline",
                    "T1_early_hazard",
                    "T2_updated_hazard",
                    "T3_diagnostic",
                )
            ],
        }
    }
