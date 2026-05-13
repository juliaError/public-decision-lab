# Method Note

This initial skeleton uses a simple intersection-based exposure screen.

## Current Method

1. Load local AOI, hazard, and administrative boundary GeoJSON files plus local road and facility GeoJSON or GeoPackage files.
2. Optionally load a local population GeoTIFF, such as a locally downloaded WorldPop raster.
3. Require AOI and hazard inputs to be polygon or multipolygon layers.
4. Require infrastructure inputs to be point, multipoint, linestring, or multilinestring layers.
5. Mark an infrastructure feature as potentially affected when it intersects both the AOI and the hazard polygon.
6. If a population raster is provided, include raster cells whose centers fall inside the hazard extent and sum their values as estimated exposed population.
7. Aggregate potentially affected roads, facilities, and estimated exposed population by administrative unit.
8. Write machine-readable outputs, a static HTML map, and a short Markdown report.

## Interpretation

The output is an exposure screen, not a damage assessment. A road or facility inside the hazard polygon may remain functional, and infrastructure outside the polygon may still be disrupted.

Population values are interpreted as estimated people per raster cell. The population result is estimated exposed population, not confirmed affected people.

Road exposure length is computed as the line length inside the AOI-hazard overlap. The unit is the input CRS unit, so projected inputs are needed for meter-like interpretation.

Facility exposure supports OSM/HOT-style hospital, clinic, school, and shelter tags. Facility counts are potential exposure counts, not confirmed service disruption.

The v0.1 demo priority score is:

```text
demo_priority_score =
  potentially affected road count
  + facilities within hazard extent count
```

This score is only a transparent sorting aid for review. It is not an official allocation decision.

## Current Scope Limits

- No remote sensing classification.
- No external API ingestion.
- No automatic WorldPop download.
- No automatic OSM or Overpass download.
- No CRS reprojection; raster and vector inputs must already match.
- No sub-cell area weighting; cell inclusion uses the raster cell center.
- No official priority scoring.
- No validated damage or service-disruption claims.
