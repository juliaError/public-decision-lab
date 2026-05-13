# OSM Infrastructure Exposure Task

## Objective

Add local OpenStreetMap/HOT-export infrastructure exposure support.

Requirements:

- accept roads as local GeoJSON or GeoPackage;
- accept facilities as local GeoJSON or GeoPackage;
- support facility types: hospital, clinic, school, shelter;
- compute road length intersecting the hazard area;
- compute number of facilities within the hazard area;
- compute facilities by type;
- compute affected facilities by admin unit;
- output `affected_roads.geojson` and `affected_facilities.geojson`;
- add tests with tiny synthetic geometries;
- update `data_sources.md` with OSM/HOT notes and limitations;
- do not call Overpass API or automatically download data in this version.

## Scope

This stage supports local files exported from OSM/HOT workflows. Automatic OSM or Overpass download adapters are future work.

## Planned Workflow

1. Add GeoPackage reading for infrastructure layers.
2. Use Shapely for infrastructure intersection and road length within the hazard extent.
3. Normalize supported OSM/HOT facility types from common tags such as `facility_type`, `amenity`, and `healthcare`.
4. Add summary fields to `impact_summary.csv`, `priority_areas.csv`, `report.md`, and `metadata.json`.
5. Add GeoJSON and GeoPackage tests with tiny synthetic geometries.

## Assumptions

- Road length is measured in the input CRS units; projected CRS is required for meter-like lengths.
- GeoJSON and GeoPackage inputs must already share the same CRS as AOI, hazard, and admin layers.
- Facilities are exposure-screened by geometry intersection with the hazard extent.
- Outputs are potentially affected infrastructure, not confirmed damage or service disruption.

## Implementation Log

### v1 Local OSM/HOT Infrastructure

- Added GeoPackage input support for infrastructure layers using standard-library SQLite plus Shapely WKB parsing.
- Kept GeoJSON input support.
- Added Shapely-based road intersection length inside AOI-hazard overlap.
- Added supported facility type normalization for `hospital`, `clinic`, `school`, and `shelter`.
- Added facility counts by type and by administrative unit.
- Added GeoJSON and GeoPackage tests with tiny synthetic geometries.
- Updated `README.md`, `method_note.md`, and `data_sources.md`.

## Verification

- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests`
- `.venv/bin/python -m pytest` passed: 5 tests.
- `.venv/bin/disaster-nowcaster run --aoi examples/sample_aoi.geojson --hazard examples/sample_flood_extent.geojson --roads examples/sample_roads.geojson --facilities examples/sample_facilities.geojson --admin examples/sample_admin_units.geojson --population examples/sample_population.tif --output outputs/demo_event --overwrite`
- Checked `outputs/demo_event/impact_summary.csv`, `metadata.json`, `report.md`, `affected_roads.geojson`, and `affected_facilities.geojson` for road length, supported facility type counts, admin facility counts, and cautious exposure language.
