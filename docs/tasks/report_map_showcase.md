# Report and Map Showcase Task

## Objective

Improve `report.md` and `map.html` so the static demo becomes the first presentable Disaster Impact Nowcaster output.

## Requirements

- `report.md` includes event metadata, data sources, estimated exposed population, affected infrastructure, top 10 priority admin units, uncertainty note, and validation checklist.
- Generate `map.html` using Folium or Leafmap.
- Map layers include AOI, hazard extent, affected facilities, and admin priority choropleth when available.
- Add tests for report generation.

## Scope

This task improves local output generation only. It does not add external APIs, satellite-data integration, official damage claims, or validated priority models.

## Planned Workflow

1. Update report rendering to include the required sections and top 10 priority table.
2. Replace the current static SVG map writer with a Folium HTML map.
3. Add Folium as a lightweight dependency.
4. Add focused report-generation tests and update CLI map/report assertions.
5. Run compile, tests, and demo command.

## Assumptions

- Event metadata is drawn from local input paths, generated file paths, and method metadata currently available in `RunConfig` and `ExposureResult`.
- Data sources are described as local user-supplied files, not authoritative external downloads.
- Admin choropleth uses the current `demo_priority_score` if priority rows are available.
- Folium-generated HTML references standard Leaflet assets; the Python workflow does not call external disaster-data APIs.

## Implementation Log

### v1 Showcase Report And Folium Map

- Expanded `report.md` with event metadata, data sources, estimated exposed population, affected infrastructure, top 10 priority admin units, uncertainty note, and validation checklist.
- Replaced the static SVG map writer with a Folium/Leaflet map.
- Added map layers for AOI, hazard extent, affected facilities, and admin priority choropleth.
- Added `folium` as a package dependency.
- Added report and map output tests in `tests/test_report.py`.
- Updated README and method note wording from static SVG to interactive Folium map.

## Verification

- `.venv/bin/python -m pip install -e ".[dev]"`
- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests`
- `.venv/bin/python -m pytest` passed: 35 tests, with one urllib3 LibreSSL warning from the local Python SSL build.
- `.venv/bin/disaster-nowcaster run --aoi examples/sample_aoi.geojson --hazard examples/sample_flood_extent.geojson --roads examples/sample_roads.geojson --facilities examples/sample_facilities.geojson --admin examples/sample_admin_units.geojson --population examples/sample_population.tif --output outputs/demo_event --overwrite`
- Checked `outputs/demo_event/report.md` and `outputs/demo_event/map.html` for required sections and layers.
