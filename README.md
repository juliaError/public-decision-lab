# Disaster Impact Nowcaster

Disaster Impact Nowcaster is a lightweight, open-source, reproducible layer for turning existing disaster hazard data and local exposure data into transparent exposure summaries and cautious decision-support reports.

It answers a narrow first question: given an AOI, a hazard polygon, administrative units, local infrastructure GeoJSON files, and an optional local population GeoTIFF, what population and infrastructure are potentially exposed, and which administrative units should be reviewed first?

It does not forecast hazards, replace official agencies, identify people, confirm damage, verify service disruption, or make official allocation decisions.

## Current Skeleton

The first version can:

- load an AOI polygon GeoJSON;
- load a hazard polygon GeoJSON;
- load administrative boundary GeoJSON;
- load infrastructure GeoJSON or GeoPackage files exported from sources such as OSM/HOT;
- load an optional local population raster GeoTIFF;
- count features that intersect both the AOI and hazard extent;
- estimate exposed population by clipping raster cells to the hazard extent;
- write `report.md`, `impact_summary.csv`, `priority_areas.csv`, affected infrastructure GeoJSON files, `map.html`, and `metadata.json`;
- run from a CLI command.

The sample files in `examples/` are tiny synthetic fixtures for testing the workflow. They are not real disaster observations and do not contain real WorldPop data.

## Install

```bash
python -m pip install -e ".[dev]"
```

The package uses `rasterio` for local GeoTIFF population rasters. The `dev` extra installs `pytest`.

## Demo

```bash
disaster-nowcaster run \
  --aoi examples/sample_aoi.geojson \
  --hazard examples/sample_flood_extent.geojson \
  --roads examples/sample_roads.geojson \
  --facilities examples/sample_facilities.geojson \
  --admin examples/sample_admin_units.geojson \
  --population examples/sample_population.tif \
  --output outputs/demo_event
```

If `outputs/demo_event` already exists from an earlier run, add `--overwrite` to regenerate the demo outputs.

Equivalent module invocation before installation:

```bash
python -m disaster_nowcaster.cli run \
  --aoi examples/sample_aoi.geojson \
  --hazard examples/sample_flood_extent.geojson \
  --roads examples/sample_roads.geojson \
  --facilities examples/sample_facilities.geojson \
  --admin examples/sample_admin_units.geojson \
  --population examples/sample_population.tif \
  --output outputs/demo_event
```

## Outputs

The demo writes an event output folder such as `outputs/demo_event/` containing:

- `impact_summary.csv`: metric/value exposure summary, including estimated exposed population when `--population` is provided;
- `priority_areas.csv`: admin-level demo ranking with exposed infrastructure counts and estimated exposed population;
- `affected_roads.geojson`: road features that intersect both AOI and hazard polygon, with input-CRS hazard-intersection length;
- `affected_facilities.geojson`: supported hospital, clinic, school, and shelter features that intersect both AOI and hazard polygon;
- `map.html`: self-contained static HTML/SVG demo map;
- `metadata.json`: input paths, method summary, and claims limit;
- `report.md`: a short human-readable Markdown report.

## Output Language

Reports use cautious terminology:

- estimated exposure, not confirmed damage;
- estimated exposed population, not confirmed affected people;
- potentially affected roads, not destroyed roads;
- facilities located within the hazard extent, not verified service disruptions.
- demo priority score, not official allocation priority.

## Limitations

- The skeleton supports local GeoJSON inputs, local GeoPackage infrastructure inputs, and local population GeoTIFF inputs.
- It supports local OSM/HOT-style GeoJSON or GeoPackage infrastructure extracts.
- It does not download WorldPop or OSM data and does not call external APIs.
- Population rasters and vector files must already use the same coordinate reference system.
- Road length is measured in input CRS units.
- The built-in geometry checks are minimal and intended for tiny synthetic fixtures, not complex real-world topology.
- It reports exposure screening only; every result requires validation against official reports and local knowledge.
- Automatic WorldPop download, reprojection, advanced geospatial operations, and validated local priority calibration are future work.

## Priority Scoring

Priority scoring is configurable and action-specific. The repository includes a baseline flood-response YAML model at `configs/priority_models/baseline_flood.yml` and scoring utilities in `src/disaster_nowcaster/scoring.py`.

Scores are decision-support indices, not official allocation rules. Default weights are illustrative baseline settings only; users should adapt weights to local objectives, constraints, data quality, and stakeholder review. Exposure does not equal confirmed damage, and all priority outputs must be locally validated before use.

The first scoring framework supports separate score families for need severity, lifeline disruption, rescue review, cash-transfer support, health support, and road repair review. Score weights are configurable, indicator directions are explicit, and missing optional indicators are flagged while available weights are renormalized. Feasibility is reported separately from need so easier delivery does not silently redefine humanitarian severity. The design rationale is documented in `priority_model_design.md`.

## Tests

```bash
python -m pytest
```

Tests use tiny synthetic GeoJSON fixtures and do not require network access. GitHub Actions runs the same test suite on push and pull request.
