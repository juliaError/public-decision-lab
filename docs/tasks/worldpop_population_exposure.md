# WorldPop Population Exposure Task

## Objective

Add a local WorldPop-style population exposure module.

Requirements:

- accept a local population raster GeoTIFF;
- clip population cells to the hazard extent;
- sum estimated exposed population;
- aggregate estimated exposed population by administrative unit;
- write population results to `impact_summary.csv`;
- add tests using a tiny synthetic raster fixture;
- update `method_note.md` with assumptions and limitations;
- do not download real WorldPop data automatically yet.

## Scope

This task supports local raster input only. A future `download_worldpop(country, year, aoi)` helper is explicitly out of scope.

## Planned Workflow

1. Add a raster-reading population module using `rasterio`.
2. Add optional `--population` CLI input so the static demo can include a local GeoTIFF while older vector-only usage remains possible.
3. Add total and admin-level population exposure fields to outputs.
4. Add a tiny synthetic GeoTIFF fixture and tests.
5. Update README and method notes with assumptions, limitations, and no-download behavior.

## Assumptions

- Raster cell values represent estimated people per cell, not confirmed people affected.
- Raster CRS and vector GeoJSON CRS must already match; v0.1 does not reproject.
- Cell inclusion uses the raster cell center point.
- Nodata and non-finite values are excluded.

## Implementation Log

### v1 Local Raster Exposure

- Added `rasterio>=1.3,<2` as the raster I/O dependency.
- Added `src/disaster_nowcaster/population.py` for local GeoTIFF exposure estimates.
- Added optional CLI input: `--population examples/sample_population.tif`.
- Added synthetic tiny rasters:
  - `examples/sample_population.tif`;
  - `tests/fixtures/population.tif`.
- Added total estimated exposed population and admin-level estimated exposed population to:
  - `impact_summary.csv`;
  - `priority_areas.csv`;
  - `report.md`;
  - `metadata.json`.
- Updated `README.md`, `data_sources.md`, `method_note.md`, and `roadmap.md`.

## Verification

- `.venv/bin/python -m pip install -e ".[dev]"` passed after allowing network access for `rasterio` and test dependencies.
- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests` passed.
- `.venv/bin/python -m pytest` passed: 3 tests passed.
- Population-enabled demo command passed:
  `disaster-nowcaster run --aoi examples/sample_aoi.geojson --hazard examples/sample_flood_extent.geojson --roads examples/sample_roads.geojson --facilities examples/sample_facilities.geojson --admin examples/sample_admin_units.geojson --population examples/sample_population.tif --output outputs/demo_event`
- Optional no-population CLI path also passed.
- Claim scan found only negative/cautious wording such as `not confirmed affected people`; no positive claims of actual victims, confirmed losses, or exact affected people were found.
