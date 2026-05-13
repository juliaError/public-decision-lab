"""Output writers for the minimal nowcaster workflow."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from disaster_nowcaster.geojson_io import write_feature_collection
from disaster_nowcaster.map import write_map_html
from disaster_nowcaster.schemas import ExposureResult, GeoJSONLayer, RunConfig


def write_outputs(
    result: ExposureResult,
    config: RunConfig,
    aoi: GeoJSONLayer,
    hazard: GeoJSONLayer,
    admin: GeoJSONLayer,
) -> list[Path]:
    """Write report, metadata, and machine-readable outputs."""

    output = config.output
    if output.exists() and any(output.iterdir()) and not config.overwrite:
        raise FileExistsError(
            f"Output directory {output} is not empty. Pass --overwrite to replace generated files."
        )

    output.mkdir(parents=True, exist_ok=True)

    paths = {
        "report": output / "report.md",
        "impact_summary": output / "impact_summary.csv",
        "priority_areas": output / "priority_areas.csv",
        "affected_roads": output / "affected_roads.geojson",
        "affected_facilities": output / "affected_facilities.geojson",
        "map": output / "map.html",
        "metadata": output / "metadata.json",
    }

    _write_impact_summary(paths["impact_summary"], result)
    _write_priority_areas(paths["priority_areas"], result)
    write_feature_collection(paths["affected_roads"], result.affected_roads)
    write_feature_collection(paths["affected_facilities"], result.affected_facilities)
    write_map_html(paths["map"], aoi=aoi, hazard=hazard, admin=admin, result=result)
    _write_metadata(paths["metadata"], result, config)
    _write_report(paths["report"], result, paths, config)

    return list(paths.values())


def render_report(result: ExposureResult, paths: dict[str, Path], config: RunConfig) -> str:
    """Render a Markdown exposure report for local decision-support review."""

    return "\n".join(
        [
            "# Disaster Impact Nowcaster Report",
            "",
            "## Summary",
            "",
            "This report provides an intersection-based exposure screening from local input files. These outputs are exposure estimates, not confirmed damage, casualties, service disruption, or official response priorities.",
            "",
            "## Event Metadata",
            "",
            f"- Generated output folder: `{config.output}`",
            "- Event type: local static exposure screening",
            "- Hazard type: user-supplied hazard extent",
            "- Validation required: yes",
            "- Claims limit: exposure estimates only; no confirmed damage or official priority decisions.",
            f"- Metadata file: `{paths['metadata'].name}`",
            "",
            "## Data Sources",
            "",
            f"- AOI: `{config.aoi}`",
            f"- Hazard extent: `{config.hazard}`",
            f"- Roads: `{config.roads}`",
            f"- Facilities: `{config.facilities}`",
            f"- Administrative units: `{config.admin}`",
            f"- Population raster: `{config.population}`" if config.population else "- Population raster: not provided",
            "",
            "All inputs are local user-supplied files. This run does not download WorldPop, OSM, satellite, or hazard data automatically.",
            "",
            "## Exposure Estimates",
            "",
            f"- AOI features loaded: {result.aoi_feature_count}",
            f"- Hazard features loaded: {result.hazard_feature_count}",
            f"- Administrative units loaded: {result.admin_feature_count}",
            f"- Road features loaded: {result.road_feature_count}",
            f"- Facility features loaded: {result.facility_feature_count}",
            f"- Hazard intersects AOI: {_yes_no(result.hazard_intersects_aoi)}",
            f"- Potentially affected roads: {result.affected_road_count}",
            f"- Potentially affected road length: {_format_number(result.affected_road_length)} input CRS units",
            f"- Facilities located within the hazard extent: {result.affected_facility_count}",
            f"- Facilities by type: {_render_facility_type_counts(result.affected_facilities_by_type)}",
            _render_population_summary_line(result),
            "",
            "## Affected Infrastructure",
            "",
            f"- Potentially affected road features: {result.affected_road_count}",
            f"- Potentially affected road length: {_format_number(result.affected_road_length)} input CRS units",
            f"- Facilities located within the hazard extent: {result.affected_facility_count}",
            f"- Facility type counts: {_render_facility_type_counts(result.affected_facilities_by_type)}",
            "",
            "## Top 10 Priority Admin Units",
            "",
            "Priority Areas are listed for review using the demo priority score. The score is a transparent sorting aid: potentially affected roads plus facilities located within the hazard extent. It is not an official allocation decision.",
            "",
            _render_priority_table(result, limit=10),
            "",
            "## Interpretation",
            "",
            "Counts are based on whether infrastructure geometries intersect both the AOI and hazard polygon. These are estimated exposure counts, not verified damage assessments.",
            "",
            "## Generated Files",
            "",
            f"- Report: `{paths['report'].name}`",
            f"- Impact summary: `{paths['impact_summary'].name}`",
            f"- Priority areas: `{paths['priority_areas'].name}`",
            f"- Potentially affected roads: `{paths['affected_roads'].name}`",
            f"- Facilities located within the hazard extent: `{paths['affected_facilities'].name}`",
            f"- Interactive map: `{paths['map'].name}`",
            f"- Metadata: `{paths['metadata'].name}`",
            "",
            "## Uncertainty Note",
            "",
            "This v0.1 demo reports exposure, not confirmed damage. Population values are estimated exposed population from raster cells, not confirmed affected people. Infrastructure inside a hazard polygon may remain functional, and infrastructure outside the polygon may still be disrupted. Outputs require validation against official reports and local knowledge.",
            "",
            "## Validation Checklist",
            "",
            "- Compare with official situation reports.",
            "- Check whether hazard timing matches the event window.",
            "- Check whether roads and facilities are complete for the AOI.",
            "- Confirm whether facilities inside the hazard extent remain functional.",
            "- Review local knowledge before using outputs for decisions.",
            "",
        ]
    )


def _write_impact_summary(path: Path, result: ExposureResult) -> None:
    rows = [
        _summary_row("aoi_feature_count", result.aoi_feature_count),
        _summary_row("hazard_feature_count", result.hazard_feature_count),
        _summary_row("admin_feature_count", result.admin_feature_count),
        _summary_row("road_feature_count", result.road_feature_count),
        _summary_row("facility_feature_count", result.facility_feature_count),
        _summary_row("hazard_intersects_aoi", result.hazard_intersects_aoi),
        _summary_row("potentially_affected_road_count", result.affected_road_count),
        _summary_row(
            "potentially_affected_road_length_input_units",
            _format_number(result.affected_road_length),
        ),
        _summary_row(
            "facilities_within_hazard_extent_count", result.affected_facility_count
        ),
    ]
    if result.population_exposure:
        rows.append(
            _summary_row(
                "estimated_exposed_population",
                _format_number(
                    result.population_exposure.estimated_exposed_population
                ),
            )
        )
        rows.append(
            _summary_row(
                "population_raster_cell_count_in_hazard",
                result.population_exposure.included_cell_count,
            )
        )
        for row in result.population_exposure.exposed_population_by_admin:
            rows.append(
                _summary_row(
                    "estimated_exposed_population_by_admin",
                    _format_number(row["estimated_exposed_population"]),
                    admin_id=row["admin_id"],
                    admin_name=row["admin_name"],
                )
            )
    for facility_type, count in result.affected_facilities_by_type.items():
        rows.append(
            _summary_row(
                "facilities_within_hazard_extent_by_type",
                count,
                facility_type=facility_type,
            )
        )
    for row in result.affected_facilities_by_admin:
        rows.append(
            _summary_row(
                "affected_facilities_by_admin",
                row["affected_facility_count"],
                admin_id=row["admin_id"],
                admin_name=row["admin_name"],
            )
        )
        for facility_type in ["hospital", "clinic", "school", "shelter"]:
            rows.append(
                _summary_row(
                    "affected_facilities_by_admin_and_type",
                    row[f"{facility_type}_count"],
                    admin_id=row["admin_id"],
                    admin_name=row["admin_name"],
                    facility_type=facility_type,
                )
            )
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["metric", "value", "admin_id", "admin_name", "facility_type"],
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_priority_areas(path: Path, result: ExposureResult) -> None:
    fieldnames = [
        "demo_rank",
        "admin_id",
        "admin_name",
        "potentially_affected_road_count",
        "facilities_within_hazard_extent_count",
        "estimated_exposed_population",
        "demo_priority_score",
        "interpretation",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result.priority_areas)


def _write_metadata(path: Path, result: ExposureResult, config: RunConfig) -> None:
    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_files": {
            "aoi": str(config.aoi),
            "hazard": str(config.hazard),
            "roads": str(config.roads),
            "facilities": str(config.facilities),
            "admin": str(config.admin),
            "population": str(config.population) if config.population else None,
        },
        "method": "Simple local vector and raster exposure screening using AOI, hazard, administrative boundary, infrastructure, and optional population files.",
        "claims_limit": "Exposure estimates only; no confirmed damage or official priority decisions.",
        "population_method": (
            "Local population GeoTIFF values are treated as estimated people per "
            "cell. Cells are included when their center falls inside the hazard "
            "extent. Vector and raster CRS must already match; no automatic "
            "WorldPop download or reprojection is performed."
        ),
        "priority_method": (
            "demo_priority_score = potentially affected road count + facilities "
            "within hazard extent count by administrative unit; decision-support "
            "sorting aid only."
        ),
        "summary": {
            "potentially_affected_road_count": result.affected_road_count,
            "potentially_affected_road_length_input_units": result.affected_road_length,
            "facilities_within_hazard_extent_count": result.affected_facility_count,
            "facilities_within_hazard_extent_by_type": result.affected_facilities_by_type,
            "affected_facilities_by_admin": result.affected_facilities_by_admin,
            "hazard_intersects_aoi": result.hazard_intersects_aoi,
            "estimated_exposed_population": (
                result.population_exposure.estimated_exposed_population
                if result.population_exposure
                else None
            ),
        },
        "population_by_admin": (
            result.population_exposure.exposed_population_by_admin
            if result.population_exposure
            else []
        ),
        "priority_areas": result.priority_areas,
        "validation_required": True,
    }
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)
        file.write("\n")


def _write_report(
    path: Path, result: ExposureResult, paths: dict[str, Path], config: RunConfig
) -> None:
    path.write_text(render_report(result, paths, config), encoding="utf-8")


def _render_priority_table(result: ExposureResult, limit: int | None = None) -> str:
    lines = [
        "| Rank | Administrative unit | Estimated exposed population | Potentially affected roads | Facilities within hazard extent | Demo score |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    rows = result.priority_areas[:limit] if limit else result.priority_areas
    for row in rows:
        lines.append(
            "| {rank} | {name} | {population} | {roads} | {facilities} | {score} |".format(
                rank=row["demo_rank"],
                name=row["admin_name"],
                population=_format_number(row.get("estimated_exposed_population", 0.0)),
                roads=row["potentially_affected_road_count"],
                facilities=row["facilities_within_hazard_extent_count"],
                score=row["demo_priority_score"],
            )
        )
    return "\n".join(lines)


def _render_population_summary_line(result: ExposureResult) -> str:
    if not result.population_exposure:
        return "- Estimated exposed population: not calculated; no population raster provided"
    return (
        "- Estimated exposed population: "
        f"{_format_number(result.population_exposure.estimated_exposed_population)}"
    )


def _summary_row(
    metric: str,
    value,
    admin_id: str | None = None,
    admin_name: str | None = None,
    facility_type: str | None = None,
) -> dict[str, object]:
    return {
        "metric": metric,
        "value": value,
        "admin_id": admin_id or "",
        "admin_name": admin_name or "",
        "facility_type": facility_type or "",
    }


def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{float(value):.2f}"


def _render_facility_type_counts(counts: dict[str, int]) -> str:
    return ", ".join(
        f"{facility_type}={counts.get(facility_type, 0)}"
        for facility_type in ["hospital", "clinic", "school", "shelter"]
    )


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"
