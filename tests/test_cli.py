import csv
import json
from pathlib import Path

from disaster_nowcaster.cli import main


FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_writes_report_and_machine_readable_outputs(tmp_path):
    output = tmp_path / "demo_event"

    exit_code = main(
        [
            "run",
            "--aoi",
            str(FIXTURES / "aoi.geojson"),
            "--hazard",
            str(FIXTURES / "hazard.geojson"),
            "--roads",
            str(FIXTURES / "roads.geojson"),
            "--facilities",
            str(FIXTURES / "facilities.geojson"),
            "--admin",
            str(FIXTURES / "admin.geojson"),
            "--population",
            str(FIXTURES / "population.tif"),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    assert (output / "report.md").exists()
    assert (output / "impact_summary.csv").exists()
    assert (output / "priority_areas.csv").exists()
    assert (output / "metadata.json").exists()
    assert (output / "map.html").exists()
    assert (output / "affected_roads.geojson").exists()
    assert (output / "affected_facilities.geojson").exists()
    assert not (output / "uncertainty_note.md").exists()

    with (output / "impact_summary.csv").open(encoding="utf-8", newline="") as file:
        rows = {row["metric"]: row["value"] for row in csv.DictReader(file)}

    assert rows["potentially_affected_road_count"] == "1"
    assert rows["potentially_affected_road_length_input_units"] == "5"
    assert rows["facilities_within_hazard_extent_count"] == "1"
    assert rows["admin_feature_count"] == "2"
    assert rows["estimated_exposed_population"] == "20"

    with (output / "impact_summary.csv").open(encoding="utf-8", newline="") as file:
        admin_population = [
            row
            for row in csv.DictReader(file)
            if row["metric"] == "estimated_exposed_population_by_admin"
        ]
    assert admin_population[0]["admin_name"] == "Synthetic West District"
    assert admin_population[0]["value"] == "10"
    assert admin_population[1]["admin_name"] == "Synthetic East District"
    assert admin_population[1]["value"] == "10"

    with (output / "impact_summary.csv").open(encoding="utf-8", newline="") as file:
        facility_types = {
            row["facility_type"]: row["value"]
            for row in csv.DictReader(file)
            if row["metric"] == "facilities_within_hazard_extent_by_type"
        }
    assert facility_types == {
        "hospital": "0",
        "clinic": "1",
        "school": "0",
        "shelter": "0",
    }

    with (output / "priority_areas.csv").open(encoding="utf-8", newline="") as file:
        priority_rows = list(csv.DictReader(file))

    assert priority_rows[0]["demo_rank"] == "1"
    assert priority_rows[0]["admin_name"] == "Synthetic East District"
    assert priority_rows[0]["demo_priority_score"] == "2"
    assert priority_rows[0]["estimated_exposed_population"] == "10.0"

    metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["claims_limit"].startswith("Exposure estimates only")
    assert metadata["validation_required"] is True
    assert metadata["summary"]["estimated_exposed_population"] == 20.0
    assert metadata["summary"]["potentially_affected_road_length_input_units"] == 5.0

    report = (output / "report.md").read_text(encoding="utf-8")
    assert "not confirmed damage" in report
    assert "Estimated exposed population: 20" in report
    assert "Priority Areas" in report

    map_html = (output / "map.html").read_text(encoding="utf-8")
    assert "requires validation" in map_html
