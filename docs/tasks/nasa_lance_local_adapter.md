# NASA LANCE Local Flood Adapter Task

## Objective

Add the first NASA LANCE-oriented adapter as a local-file adapter. It should accept a user-supplied local flood raster GeoTIFF and convert thresholded flood pixels into a local hazard GeoJSON for the existing pipeline.

## Scope

This task does not download NASA LANCE data, call APIs, classify satellite imagery, or claim official flood mapping. It only supports local raster-to-GeoJSON preparation.

## Planned Workflow

1. Add `LocalNasaLanceFloodAdapter`.
2. Polygonize raster cells meeting a configurable flood threshold.
3. Write a local hazard GeoJSON.
4. Return `AdapterResult` with NASA-style metadata and limitations.
5. Add tiny synthetic raster tests.
6. Update adapter documentation and data-source notes.

## Assumptions

- Raster values greater than or equal to `flood_value` are treated as flood pixels for screening.
- Raster CRS is not reprojected; output coordinates follow the raster transform/CRS coordinate space.
- Users must validate timing, CRS, flood-class semantics, and product quality before operational use.

## Implementation Log

### v1 Local NASA LANCE-Style Raster Adapter

- Added `LocalNasaLanceFloodAdapter`.
- Reads a local GeoTIFF raster band.
- Polygonizes cells with values greater than or equal to `flood_value`.
- Writes a local hazard GeoJSON.
- Returns adapter metadata with source limitations and `auto_downloaded=False`.
- Added tests with a tiny synthetic raster fixture generated at test time.
- Updated adapter contract, README, method note, and data-source notes.

## Verification

- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests`
- `.venv/bin/python -m pytest` passed: 41 tests, with one urllib3 LibreSSL warning from the local Python SSL build.
- `.venv/bin/disaster-nowcaster run --aoi examples/sample_aoi.geojson --hazard examples/sample_flood_extent.geojson --roads examples/sample_roads.geojson --facilities examples/sample_facilities.geojson --admin examples/sample_admin_units.geojson --population examples/sample_population.tif --output outputs/demo_event --overwrite`
