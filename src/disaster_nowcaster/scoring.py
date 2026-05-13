"""Transparent demo priority scoring for the static v0.1 workflow."""

from __future__ import annotations

from disaster_nowcaster.geometry import extract_polygons, geometry_intersects_any_polygon
from disaster_nowcaster.schemas import Feature, GeoJSONLayer, PriorityRow


def build_priority_rows(
    admin: GeoJSONLayer,
    affected_roads: list[Feature],
    affected_facilities: list[Feature],
    exposed_population_by_admin: list[PriorityRow] | None = None,
) -> list[PriorityRow]:
    """Build admin-level demo priority rows from exposed infrastructure counts.

    The v0.1 score is a transparent sorting aid:
    affected road count + affected facility count. It is not an official
    allocation decision and does not represent confirmed damage.
    """

    population_lookup = {
        str(row["admin_id"]): row for row in (exposed_population_by_admin or [])
    }
    rows: list[PriorityRow] = []
    for index, feature in enumerate(admin.features, start=1):
        polygons = extract_polygons(feature["geometry"])
        road_count = _count_features_in_polygons(affected_roads, polygons)
        facility_count = _count_features_in_polygons(affected_facilities, polygons)
        score = road_count + facility_count
        properties = feature.get("properties", {})
        admin_id = properties.get("id", f"admin_{index}")
        population_row = population_lookup.get(str(admin_id), {})
        rows.append(
            {
                "admin_id": admin_id,
                "admin_name": properties.get("name", f"Admin unit {index}"),
                "potentially_affected_road_count": road_count,
                "facilities_within_hazard_extent_count": facility_count,
                "estimated_exposed_population": float(
                    population_row.get("estimated_exposed_population", 0.0)
                ),
                "demo_priority_score": score,
                "demo_rank": 0,
                "interpretation": (
                    "Decision-support sorting aid only; exposure count, not confirmed damage."
                ),
            }
        )

    rows.sort(
        key=lambda row: (
            -row["demo_priority_score"],
            -row["facilities_within_hazard_extent_count"],
            -row["potentially_affected_road_count"],
            str(row["admin_name"]),
        )
    )
    for rank, row in enumerate(rows, start=1):
        row["demo_rank"] = rank
    return rows


def _count_features_in_polygons(features: list[Feature], polygons: list) -> int:
    return sum(
        1
        for feature in features
        if geometry_intersects_any_polygon(feature["geometry"], polygons)
    )
