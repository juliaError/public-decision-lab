# Adapter Contract Task

## Objective

Define the first adapter contract so future NASA LANCE, Copernicus GFM, GDACS, WorldPop, and OSM/HOT integrations can plug into the stable local-file pipeline.

## Scope

This stage defines interfaces, metadata, a lightweight event object, and a local hazard adapter. It does not call external APIs, download real disaster data, classify satellite imagery, or change the public project scope.

## Planned Workflow

1. Add event metadata structures.
2. Add base adapter contracts for event, hazard, population, and infrastructure sources.
3. Add a local hazard adapter that wraps an existing local GeoJSON hazard file.
4. Document the adapter contract and future integration path.
5. Add deterministic tests using existing tiny fixtures.

## Assumptions

- The core pipeline should continue to consume local standardized files.
- Adapters should return local paths and metadata/provenance, not directly mutate analysis results.
- Real NASA/Copernicus/GDACS adapters are future work.

## Implementation Log

### v1 Local Adapter Contract

- Added `DisasterEvent` and `EventWindow` metadata structures.
- Added `AdapterMetadata`, `AdapterResult`, and protocol contracts for event, hazard, population, and infrastructure adapters.
- Added `LocalHazardAdapter` for existing local hazard GeoJSON files.
- Added `docs/adapter_contract.md`.
- Added adapter tests using tiny local fixtures.
- Updated README, method note, and data-source notes.

## Verification

- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests`
- `.venv/bin/python -m pytest` passed: 39 tests, with one urllib3 LibreSSL warning from the local Python SSL build.
- `.venv/bin/disaster-nowcaster run --aoi examples/sample_aoi.geojson --hazard examples/sample_flood_extent.geojson --roads examples/sample_roads.geojson --facilities examples/sample_facilities.geojson --admin examples/sample_admin_units.geojson --population examples/sample_population.tif --output outputs/demo_event --overwrite`
