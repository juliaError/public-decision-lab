import sqlite3
from pathlib import Path

from shapely import wkb
from shapely.geometry import LineString, Point

from disaster_nowcaster.admin import load_admin_units
from disaster_nowcaster.aoi import load_aoi
from disaster_nowcaster.exposure import compute_exposure
from disaster_nowcaster.hazard import load_hazard
from disaster_nowcaster.infrastructure import load_infrastructure


FIXTURES = Path(__file__).parent / "fixtures"


def test_osm_geojson_infrastructure_exposure_outputs_lengths_and_types():
    result = compute_exposure(
        aoi=load_aoi(FIXTURES / "aoi.geojson"),
        hazard=load_hazard(FIXTURES / "hazard.geojson"),
        roads=load_infrastructure(FIXTURES / "roads.geojson", name="roads"),
        facilities=load_infrastructure(FIXTURES / "facilities.geojson", name="facilities"),
        admin=load_admin_units(FIXTURES / "admin.geojson"),
    )

    assert result.affected_road_count == 1
    assert result.affected_road_length == 5.0
    assert result.affected_roads[0]["properties"]["hazard_intersection_length"] == 5.0
    assert result.affected_facilities_by_type == {
        "hospital": 0,
        "clinic": 1,
        "school": 0,
        "shelter": 0,
    }
    assert result.affected_facilities_by_admin[0]["admin_name"] == "Synthetic West District"
    assert result.affected_facilities_by_admin[0]["affected_facility_count"] == 0
    assert result.affected_facilities_by_admin[1]["admin_name"] == "Synthetic East District"
    assert result.affected_facilities_by_admin[1]["affected_facility_count"] == 1


def test_osm_geopackage_infrastructure_inputs_are_supported(tmp_path):
    roads_path = tmp_path / "roads.gpkg"
    facilities_path = tmp_path / "facilities.gpkg"
    _write_gpkg(
        roads_path,
        table_name="roads",
        geometry_type="LINESTRING",
        rows=[
            {
                "id": "affected_road",
                "geometry": LineString([(2, 5), (9, 5)]),
            }
        ],
    )
    _write_gpkg(
        facilities_path,
        table_name="facilities",
        geometry_type="POINT",
        rows=[
            {
                "id": "hospital_in_hazard",
                "amenity": "hospital",
                "geometry": Point(6, 5),
            },
            {
                "id": "unsupported_cafe",
                "amenity": "cafe",
                "geometry": Point(6, 6),
            },
        ],
    )

    result = compute_exposure(
        aoi=load_aoi(FIXTURES / "aoi.geojson"),
        hazard=load_hazard(FIXTURES / "hazard.geojson"),
        roads=load_infrastructure(roads_path, name="roads"),
        facilities=load_infrastructure(facilities_path, name="facilities"),
        admin=load_admin_units(FIXTURES / "admin.geojson"),
    )

    assert result.road_feature_count == 1
    assert result.facility_feature_count == 1
    assert result.affected_road_length == 5.0
    assert result.affected_facilities_by_type["hospital"] == 1
    assert result.affected_facilities[0]["properties"]["facility_type"] == "hospital"


def _write_gpkg(path, table_name, geometry_type, rows):
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE gpkg_contents (table_name TEXT PRIMARY KEY, data_type TEXT NOT NULL)"
        )
        connection.execute(
            "CREATE TABLE gpkg_geometry_columns (table_name TEXT, column_name TEXT, geometry_type_name TEXT)"
        )
        connection.execute(
            "INSERT INTO gpkg_contents (table_name, data_type) VALUES (?, 'features')",
            (table_name,),
        )
        connection.execute(
            "INSERT INTO gpkg_geometry_columns VALUES (?, 'geom', ?)",
            (table_name, geometry_type),
        )
        connection.execute(
            f'CREATE TABLE "{table_name}" (fid INTEGER PRIMARY KEY, id TEXT, amenity TEXT, geom BLOB)'
        )
        for fid, row in enumerate(rows, start=1):
            connection.execute(
                f'INSERT INTO "{table_name}" (fid, id, amenity, geom) VALUES (?, ?, ?, ?)',
                (
                    fid,
                    row.get("id"),
                    row.get("amenity"),
                    _gpkg_geometry_blob(row["geometry"]),
                ),
            )


def _gpkg_geometry_blob(geometry):
    header = b"GP" + bytes([0, 1]) + (4326).to_bytes(4, "little", signed=True)
    return header + wkb.dumps(geometry, byte_order=1)
