"""Minimal geometry predicates for small GeoJSON fixtures.

This module is intentionally limited. It supports Point, MultiPoint,
LineString, MultiLineString, Polygon, and MultiPolygon geometries well enough
for the first synthetic test workflow. Future versions should replace this
with a full geospatial backend before handling complex real-world topology.
"""

from __future__ import annotations

from typing import Any, Iterable

Coordinate = tuple[float, float]
Ring = list[Coordinate]
Polygon = list[Ring]

EPSILON = 1e-9


def geometry_intersects_any_polygon(
    geometry: dict[str, Any], polygons: list[Polygon]
) -> bool:
    """Return whether a GeoJSON geometry intersects at least one polygon."""

    return any(geometry_intersects_polygon(geometry, polygon) for polygon in polygons)


def polygons_intersect_any(left: list[Polygon], right: list[Polygon]) -> bool:
    """Return whether any polygon from two collections intersects."""

    return any(polygon_intersects_polygon(a, b) for a in left for b in right)


def extract_polygons(geometry: dict[str, Any]) -> list[Polygon]:
    """Extract Polygon or MultiPolygon coordinates from a GeoJSON geometry."""

    geom_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geom_type == "Polygon":
        return [_polygon_from_coordinates(coordinates)]
    if geom_type == "MultiPolygon":
        return [_polygon_from_coordinates(item) for item in coordinates]
    raise ValueError(f"Expected Polygon or MultiPolygon geometry, got {geom_type!r}.")


def geometry_intersects_polygon(geometry: dict[str, Any], polygon: Polygon) -> bool:
    """Return whether a supported GeoJSON geometry intersects one polygon."""

    geom_type = geometry.get("type")
    coordinates = geometry.get("coordinates")

    if geom_type == "Point":
        return point_in_polygon(_point(coordinates), polygon)
    if geom_type == "MultiPoint":
        return any(point_in_polygon(_point(point), polygon) for point in coordinates)
    if geom_type == "LineString":
        return line_intersects_polygon(_line(coordinates), polygon)
    if geom_type == "MultiLineString":
        return any(line_intersects_polygon(_line(line), polygon) for line in coordinates)
    if geom_type == "Polygon":
        return polygon_intersects_polygon(_polygon_from_coordinates(coordinates), polygon)
    if geom_type == "MultiPolygon":
        return any(
            polygon_intersects_polygon(_polygon_from_coordinates(item), polygon)
            for item in coordinates
        )

    raise ValueError(f"Unsupported GeoJSON geometry type: {geom_type!r}.")


def line_intersects_polygon(line: list[Coordinate], polygon: Polygon) -> bool:
    """Return whether a line intersects a polygon."""

    if any(point_in_polygon(point, polygon) for point in line):
        return True

    for segment in _segments(line):
        for edge in _polygon_edges(polygon):
            if segments_intersect(segment[0], segment[1], edge[0], edge[1]):
                return True
    return False


def polygon_intersects_polygon(left: Polygon, right: Polygon) -> bool:
    """Return whether two polygons intersect."""

    left_outer = left[0]
    right_outer = right[0]

    if any(point_in_polygon(point, right) for point in left_outer):
        return True
    if any(point_in_polygon(point, left) for point in right_outer):
        return True

    for left_edge in _polygon_edges(left):
        for right_edge in _polygon_edges(right):
            if segments_intersect(left_edge[0], left_edge[1], right_edge[0], right_edge[1]):
                return True
    return False


def point_in_polygon(point: Coordinate, polygon: Polygon) -> bool:
    """Return whether a point is inside a polygon, counting boundary as inside."""

    outer = polygon[0]
    if not _point_in_ring(point, outer):
        return False
    for hole in polygon[1:]:
        if _point_in_ring(point, hole):
            return False
    return True


def segments_intersect(
    a: Coordinate, b: Coordinate, c: Coordinate, d: Coordinate
) -> bool:
    """Return whether two line segments intersect."""

    o1 = _orientation(a, b, c)
    o2 = _orientation(a, b, d)
    o3 = _orientation(c, d, a)
    o4 = _orientation(c, d, b)

    if o1 * o2 < 0 and o3 * o4 < 0:
        return True
    return (
        _is_zero(o1)
        and _on_segment(a, c, b)
        or _is_zero(o2)
        and _on_segment(a, d, b)
        or _is_zero(o3)
        and _on_segment(c, a, d)
        or _is_zero(o4)
        and _on_segment(c, b, d)
    )


def _polygon_from_coordinates(coordinates: Iterable[Any]) -> Polygon:
    return [_line(ring) for ring in coordinates]


def _line(coordinates: Iterable[Any]) -> list[Coordinate]:
    return [_point(point) for point in coordinates]


def _point(coordinates: Iterable[Any]) -> Coordinate:
    x, y = coordinates
    return float(x), float(y)


def _polygon_edges(polygon: Polygon) -> list[tuple[Coordinate, Coordinate]]:
    edges: list[tuple[Coordinate, Coordinate]] = []
    for ring in polygon:
        edges.extend(_segments(ring))
    return edges


def _segments(line: list[Coordinate]) -> list[tuple[Coordinate, Coordinate]]:
    return list(zip(line, line[1:]))


def _point_in_ring(point: Coordinate, ring: Ring) -> bool:
    x, y = point
    inside = False

    for start, end in _segments(ring):
        if _on_segment(start, point, end):
            return True

        x1, y1 = start
        x2, y2 = end
        crosses = (y1 > y) != (y2 > y)
        if crosses:
            x_at_y = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x <= x_at_y:
                inside = not inside

    return inside


def _orientation(a: Coordinate, b: Coordinate, c: Coordinate) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a: Coordinate, b: Coordinate, c: Coordinate) -> bool:
    return (
        min(a[0], c[0]) - EPSILON <= b[0] <= max(a[0], c[0]) + EPSILON
        and min(a[1], c[1]) - EPSILON <= b[1] <= max(a[1], c[1]) + EPSILON
        and _is_zero(_orientation(a, b, c))
    )


def _is_zero(value: float) -> bool:
    return abs(value) <= EPSILON
