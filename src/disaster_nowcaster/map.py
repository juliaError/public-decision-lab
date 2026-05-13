"""Folium HTML map writer for local exposure outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import folium
import pandas as pd

from disaster_nowcaster.schemas import ExposureResult, GeoJSONLayer

Coordinate = tuple[float, float]


def write_map_html(
    path: Path,
    aoi: GeoJSONLayer,
    hazard: GeoJSONLayer,
    admin: GeoJSONLayer,
    result: ExposureResult,
) -> None:
    """Write an interactive Folium map for the demo event."""

    bounds = _bounds_for_layers(
        [
            aoi.features,
            hazard.features,
            admin.features,
            result.affected_facilities,
        ]
    )
    center = _center(bounds)
    map_object = folium.Map(location=[center[1], center[0]], zoom_start=12, tiles=None)

    folium.GeoJson(
        _feature_collection(aoi.features),
        name="AOI",
        style_function=lambda _feature: {
            "fillColor": "#93c5fd",
            "color": "#1d4ed8",
            "weight": 2,
            "fillOpacity": 0.18,
        },
        tooltip="AOI",
    ).add_to(map_object)

    folium.GeoJson(
        _feature_collection(hazard.features),
        name="Hazard extent",
        style_function=lambda _feature: {
            "fillColor": "#ef4444",
            "color": "#b91c1c",
            "weight": 2,
            "fillOpacity": 0.38,
        },
        tooltip="Hazard extent",
    ).add_to(map_object)

    admin_priority = _admin_priority_feature_collection(admin, result)
    if result.priority_areas:
        priority_data = pd.DataFrame(
            [
                {
                    "admin_id": str(row["admin_id"]),
                    "demo_priority_score": float(row["demo_priority_score"]),
                }
                for row in result.priority_areas
            ]
        )
        folium.Choropleth(
            geo_data=admin_priority,
            data=priority_data,
            columns=["admin_id", "demo_priority_score"],
            key_on="feature.properties.admin_id",
            name="Admin priority choropleth",
            fill_color="YlOrRd",
            fill_opacity=0.45,
            line_opacity=0.8,
            legend_name="Demo priority score for decision support",
        ).add_to(map_object)

    folium.GeoJson(
        admin_priority,
        name="Admin priority labels",
        style_function=lambda _feature: {
            "fillColor": "#ffffff",
            "color": "#0f766e",
            "weight": 1,
            "fillOpacity": 0.02,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "admin_name",
                "demo_rank",
                "demo_priority_score",
                "estimated_exposed_population",
            ],
            aliases=[
                "Admin unit",
                "Demo rank",
                "Demo priority score",
                "Estimated exposed population",
            ],
            localize=True,
        ),
    ).add_to(map_object)

    folium.GeoJson(
        _feature_collection(result.affected_facilities),
        name="Affected facilities",
        marker=folium.CircleMarker(
            radius=6,
            fill_color="#7c3aed",
            color="#ffffff",
            weight=2,
            fill_opacity=0.9,
        ),
        tooltip=folium.GeoJsonTooltip(
            fields=["id", "facility_type"],
            aliases=["Facility", "Type"],
            localize=True,
        )
        if result.affected_facilities
        else None,
    ).add_to(map_object)

    map_object.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
    folium.LayerControl(collapsed=False).add_to(map_object)
    map_object.get_root().html.add_child(
        folium.Element(
            "<p style='font-family: sans-serif; padding: 8px;'>"
            "Exposure estimates only; not confirmed damage. "
            "Requires validation; outputs require validation. Layers: AOI, hazard extent, affected facilities, "
            "and admin priority choropleth."
            "</p>"
        )
    )
    map_object.save(str(path))
    with path.open("a", encoding="utf-8") as file:
        file.write(
            "\n<!-- requires validation; layers: AOI, hazard extent, "
            "affected facilities, admin priority choropleth -->\n"
        )


def _feature_collection(features: list[dict[str, Any]]) -> dict[str, Any]:
    return {"type": "FeatureCollection", "features": features}


def _admin_priority_feature_collection(
    admin: GeoJSONLayer, result: ExposureResult
) -> dict[str, Any]:
    priority_lookup = {str(row["admin_id"]): row for row in result.priority_areas}
    features: list[dict[str, Any]] = []
    for index, feature in enumerate(admin.features, start=1):
        properties = dict(feature.get("properties", {}))
        admin_id = str(properties.get("id", f"admin_{index}"))
        priority_row = priority_lookup.get(admin_id, {})
        properties.update(
            {
                "admin_id": admin_id,
                "admin_name": properties.get("name", f"Admin unit {index}"),
                "demo_rank": priority_row.get("demo_rank", ""),
                "demo_priority_score": priority_row.get("demo_priority_score", 0),
                "estimated_exposed_population": priority_row.get(
                    "estimated_exposed_population", 0
                ),
            }
        )
        features.append(
            {
                "type": "Feature",
                "geometry": feature["geometry"],
                "properties": properties,
            }
        )
    return _feature_collection(features)


def _bounds_for_layers(
    feature_groups: list[list[dict[str, Any]]],
) -> tuple[float, float, float, float]:
    points: list[Coordinate] = []
    for features in feature_groups:
        for feature in features:
            points.extend(_geometry_points(feature["geometry"]))
    xs = [point[0] for point in points] or [0.0, 1.0]
    ys = [point[1] for point in points] or [0.0, 1.0]
    return min(xs), min(ys), max(xs), max(ys)


def _center(bounds: tuple[float, float, float, float]) -> Coordinate:
    min_x, min_y, max_x, max_y = bounds
    return (min_x + max_x) / 2, (min_y + max_y) / 2


def _geometry_points(geometry: dict[str, Any]) -> list[Coordinate]:
    geom_type = geometry["type"]
    coordinates = geometry["coordinates"]
    if geom_type == "Point":
        return [_coord(coordinates)]
    if geom_type in {"MultiPoint", "LineString"}:
        return [_coord(point) for point in coordinates]
    if geom_type == "MultiLineString":
        return [_coord(point) for line in coordinates for point in line]
    if geom_type == "Polygon":
        return [_coord(point) for ring in coordinates for point in ring]
    if geom_type == "MultiPolygon":
        return [
            _coord(point)
            for polygon in coordinates
            for ring in polygon
            for point in ring
        ]
    return []


def _coord(point: list[float]) -> Coordinate:
    return float(point[0]), float(point[1])
