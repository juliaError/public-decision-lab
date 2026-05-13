"""Self-contained static HTML map writer for small GeoJSON demo files."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from disaster_nowcaster.geometry import extract_polygons
from disaster_nowcaster.schemas import ExposureResult, GeoJSONLayer

Coordinate = tuple[float, float]


def write_map_html(
    path: Path,
    aoi: GeoJSONLayer,
    hazard: GeoJSONLayer,
    admin: GeoJSONLayer,
    result: ExposureResult,
) -> None:
    """Write a small standalone HTML/SVG map for the demo event."""

    bounds = _bounds_for_layers(
        [
            aoi.features,
            hazard.features,
            admin.features,
            result.affected_roads,
            result.affected_facilities,
        ]
    )
    svg = _render_svg(bounds, aoi, hazard, admin, result)
    payload = {
        "aoi": str(aoi.path),
        "hazard": str(hazard.path),
        "admin": str(admin.path),
        "affected_road_count": result.affected_road_count,
        "affected_facility_count": result.affected_facility_count,
    }
    path.write_text(
        "\n".join(
            [
                "<!doctype html>",
                '<html lang="en">',
                "<head>",
                '<meta charset="utf-8">',
                '<meta name="viewport" content="width=device-width, initial-scale=1">',
                "<title>Disaster Impact Nowcaster Demo Map</title>",
                "<style>",
                "body { font-family: Arial, sans-serif; margin: 24px; color: #1f2933; }",
                ".map-wrap { max-width: 920px; }",
                "svg { width: 100%; height: auto; border: 1px solid #ccd4dd; background: #f8fafc; }",
                ".legend { display: flex; flex-wrap: wrap; gap: 12px; margin: 12px 0; font-size: 14px; }",
                ".swatch { display: inline-block; width: 14px; height: 14px; margin-right: 5px; vertical-align: -2px; border: 1px solid #64748b; }",
                "pre { background: #f1f5f9; padding: 12px; overflow: auto; }",
                "</style>",
                "</head>",
                "<body>",
                '<main class="map-wrap">',
                "<h1>Disaster Impact Nowcaster Demo Map</h1>",
                "<p>This static map shows estimated exposure from local sample files. It is not confirmed damage and requires validation.</p>",
                '<div class="legend">',
                '<span><span class="swatch" style="background:#dbeafe"></span>AOI</span>',
                '<span><span class="swatch" style="background:#fecaca"></span>Hazard extent</span>',
                '<span><span class="swatch" style="background:#e0f2fe"></span>Admin units</span>',
                '<span><span class="swatch" style="background:#f97316"></span>Potentially affected roads</span>',
                '<span><span class="swatch" style="background:#7c3aed"></span>Facilities within hazard extent</span>',
                "</div>",
                svg,
                "<h2>Map Metadata</h2>",
                f"<pre>{html.escape(json.dumps(payload, indent=2))}</pre>",
                "</main>",
                "</body>",
                "</html>",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _render_svg(
    bounds: tuple[float, float, float, float],
    aoi: GeoJSONLayer,
    hazard: GeoJSONLayer,
    admin: GeoJSONLayer,
    result: ExposureResult,
) -> str:
    width = 900
    height = 620
    padding = 36

    def project(point: Coordinate) -> Coordinate:
        min_x, min_y, max_x, max_y = bounds
        scale_x = (width - padding * 2) / max(max_x - min_x, 1e-9)
        scale_y = (height - padding * 2) / max(max_y - min_y, 1e-9)
        scale = min(scale_x, scale_y)
        x = padding + (point[0] - min_x) * scale
        y = height - padding - (point[1] - min_y) * scale
        return x, y

    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Static exposure map">',
    ]
    parts.extend(_polygon_paths(aoi.features, project, "#bfdbfe", "#2563eb", 0.22, 2))
    parts.extend(_polygon_paths(admin.features, project, "#e0f2fe", "#0369a1", 0.18, 1))
    parts.extend(_polygon_paths(hazard.features, project, "#fca5a5", "#dc2626", 0.42, 2))
    parts.extend(_line_paths(result.affected_roads, project))
    parts.extend(_point_marks(result.affected_facilities, project))
    parts.append("</svg>")
    return "\n".join(parts)


def _polygon_paths(features, project, fill, stroke, opacity, stroke_width):
    paths = []
    for feature in features:
        for polygon in extract_polygons(feature["geometry"]):
            outer = " ".join(_format_point(project(point)) for point in polygon[0])
            paths.append(
                f'<polygon points="{outer}" fill="{fill}" fill-opacity="{opacity}" '
                f'stroke="{stroke}" stroke-width="{stroke_width}" />'
            )
    return paths


def _line_paths(features, project):
    paths = []
    for feature in features:
        geometry = feature["geometry"]
        line_sets = []
        if geometry["type"] == "LineString":
            line_sets = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            line_sets = geometry["coordinates"]
        for line in line_sets:
            points = " ".join(_format_point(project((float(x), float(y)))) for x, y in line)
            paths.append(
                f'<polyline points="{points}" fill="none" stroke="#f97316" '
                'stroke-width="5" stroke-linecap="round" />'
            )
    return paths


def _point_marks(features, project):
    marks = []
    for feature in features:
        geometry = feature["geometry"]
        point_sets = []
        if geometry["type"] == "Point":
            point_sets = [geometry["coordinates"]]
        elif geometry["type"] == "MultiPoint":
            point_sets = geometry["coordinates"]
        for x, y in point_sets:
            px, py = project((float(x), float(y)))
            marks.append(
                f'<circle cx="{px:.2f}" cy="{py:.2f}" r="7" fill="#7c3aed" '
                'stroke="#ffffff" stroke-width="2" />'
            )
    return marks


def _bounds_for_layers(feature_groups: list[list[dict[str, Any]]]) -> tuple[float, float, float, float]:
    points: list[Coordinate] = []
    for features in feature_groups:
        for feature in features:
            points.extend(_geometry_points(feature["geometry"]))
    xs = [point[0] for point in points] or [0.0, 1.0]
    ys = [point[1] for point in points] or [0.0, 1.0]
    return min(xs), min(ys), max(xs), max(ys)


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


def _format_point(point: Coordinate) -> str:
    return f"{point[0]:.2f},{point[1]:.2f}"
