"""Intersection-based exposure calculations."""

from __future__ import annotations

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

from disaster_nowcaster.geometry import (
    extract_polygons,
    polygons_intersect_any,
)
from disaster_nowcaster.infrastructure import normalize_facility_type
from disaster_nowcaster.scoring import build_priority_rows
from disaster_nowcaster.schemas import (
    ExposureResult,
    Feature,
    GeoJSONLayer,
    PopulationExposureResult,
)


def compute_exposure(
    aoi: GeoJSONLayer,
    hazard: GeoJSONLayer,
    roads: GeoJSONLayer,
    facilities: GeoJSONLayer,
    admin: GeoJSONLayer,
    population_exposure: PopulationExposureResult | None = None,
) -> ExposureResult:
    """Compute minimal infrastructure exposure counts.

    A feature is marked potentially affected when it intersects the AOI and the
    hazard extent. This screening estimate is exposure, not confirmed damage.
    """

    aoi_polygons = _layer_polygons(aoi)
    hazard_polygons = _layer_polygons(hazard)
    hazard_intersects_aoi = polygons_intersect_any(aoi_polygons, hazard_polygons)
    exposure_area = _layer_union(aoi).intersection(_layer_union(hazard))

    affected_roads = (
        _affected_road_features(roads.features, exposure_area)
        if hazard_intersects_aoi
        else []
    )
    affected_facilities = (
        _affected_facility_features(facilities.features, exposure_area)
        if hazard_intersects_aoi
        else []
    )
    affected_road_length = sum(
        feature["properties"]["hazard_intersection_length"] for feature in affected_roads
    )
    affected_facilities_by_type = _facility_counts_by_type(affected_facilities)
    affected_facilities_by_admin = _facility_counts_by_admin(admin, affected_facilities)
    population_by_admin = (
        population_exposure.exposed_population_by_admin if population_exposure else None
    )
    priority_areas = build_priority_rows(
        admin, affected_roads, affected_facilities, population_by_admin
    )

    return ExposureResult(
        aoi_feature_count=len(aoi.features),
        hazard_feature_count=len(hazard.features),
        admin_feature_count=len(admin.features),
        road_feature_count=len(roads.features),
        facility_feature_count=len(facilities.features),
        affected_road_count=len(affected_roads),
        affected_road_length=affected_road_length,
        affected_facility_count=len(affected_facilities),
        affected_facilities_by_type=affected_facilities_by_type,
        affected_facilities_by_admin=affected_facilities_by_admin,
        affected_roads=affected_roads,
        affected_facilities=affected_facilities,
        priority_areas=priority_areas,
        hazard_intersects_aoi=hazard_intersects_aoi,
        population_exposure=population_exposure,
    )


def _layer_polygons(layer: GeoJSONLayer) -> list:
    polygons = []
    for feature in layer.features:
        polygons.extend(extract_polygons(feature["geometry"]))
    return polygons


def _layer_union(layer: GeoJSONLayer):
    return unary_union([shape(feature["geometry"]) for feature in layer.features])


def _affected_road_features(features: list[Feature], exposure_area) -> list[Feature]:
    affected: list[Feature] = []
    for feature in features:
        geometry = shape(feature["geometry"])
        exposed_geometry = geometry.intersection(exposure_area)
        exposed_length = float(exposed_geometry.length)
        if exposed_length <= 0:
            continue
        copied = _copy_feature(feature)
        copied["properties"]["hazard_intersection_length"] = exposed_length
        copied["properties"]["length_units"] = "input_crs_units"
        affected.append(copied)
    return affected


def _affected_facility_features(features: list[Feature], exposure_area) -> list[Feature]:
    affected: list[Feature] = []
    for feature in features:
        if not shape(feature["geometry"]).intersects(exposure_area):
            continue
        facility_type = normalize_facility_type(feature)
        if not facility_type:
            continue
        copied = _copy_feature(feature)
        copied["properties"]["facility_type"] = facility_type
        affected.append(copied)
    return affected


def _facility_counts_by_type(features: list[Feature]) -> dict[str, int]:
    counts = {"hospital": 0, "clinic": 0, "school": 0, "shelter": 0}
    for feature in features:
        facility_type = normalize_facility_type(feature)
        if facility_type:
            counts[facility_type] += 1
    return counts


def _facility_counts_by_admin(
    admin: GeoJSONLayer, affected_facilities: list[Feature]
) -> list[dict]:
    rows: list[dict] = []
    for index, feature in enumerate(admin.features, start=1):
        properties = feature.get("properties", {})
        admin_geometry = shape(feature["geometry"])
        facilities = [
            item
            for item in affected_facilities
            if shape(item["geometry"]).intersects(admin_geometry)
        ]
        counts = _facility_counts_by_type(facilities)
        rows.append(
            {
                "admin_id": properties.get("id", f"admin_{index}"),
                "admin_name": properties.get("name", f"Admin unit {index}"),
                "affected_facility_count": len(facilities),
                "hospital_count": counts["hospital"],
                "clinic_count": counts["clinic"],
                "school_count": counts["school"],
                "shelter_count": counts["shelter"],
            }
        )
    return rows


def _copy_feature(feature: Feature) -> Feature:
    return {
        "type": feature["type"],
        "geometry": mapping(shape(feature["geometry"])),
        "properties": dict(feature.get("properties", {})),
    }
