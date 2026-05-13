from pathlib import Path

from disaster_nowcaster.cli import main


FIXTURES = Path(__file__).parent / "fixtures"


def test_report_contains_showcase_sections(tmp_path):
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
    report = (output / "report.md").read_text(encoding="utf-8")

    assert "## Event Metadata" in report
    assert "## Data Sources" in report
    assert "## Exposure Estimates" in report
    assert "## Affected Infrastructure" in report
    assert "## Top 10 Priority Admin Units" in report
    assert "## Uncertainty Note" in report
    assert "## Validation Checklist" in report
    assert "Estimated exposed population: 20" in report
    assert "Potentially affected road features: 1" in report
    assert "Facilities located within the hazard extent: 1" in report
    assert "Synthetic East District" in report
    assert "not confirmed damage" in report
    assert "Validation required: yes" in report


def test_folium_map_contains_required_layers(tmp_path):
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
    map_html = (output / "map.html").read_text(encoding="utf-8")

    assert "leaflet" in map_html.lower()
    assert "AOI" in map_html
    assert "Hazard extent" in map_html
    assert "Affected facilities" in map_html
    assert "Admin priority choropleth" in map_html
    assert "Requires validation" in map_html
