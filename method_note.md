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

## Priority Scoring Framework

The scoring framework is grounded in established disaster-risk and humanitarian-analysis concepts: hazard, exposure, vulnerability, capacity, lack of coping capacity, intersectoral needs severity, impact-based forecasting, anticipatory-action trigger review, community lifelines, and multi-criteria decision analysis.

The project now supports configurable score families rather than one universal priority score:

- need severity;
- lifeline disruption;
- rescue review priority;
- cash-transfer support priority;
- health support priority;
- road repair review priority.

Scores use explicit weights from YAML configuration files, with `configs/priority_models/baseline_flood.yml` as an illustrative baseline. The YAML config includes an indicator catalog with concept, entity level, direction, role, unit, interpretation note, and sensitivity or privacy note. The implementation normalizes indicators within the event using min-max normalization. If all non-missing indicator values are equal, the normalized value is `0.0` under the `zero_discriminatory_contribution` policy: the indicator provides no within-event ranking information, not zero underlying risk.

Weights are normative choices, not scientific facts. They should be reviewed locally, documented in reports, and sensitivity-tested before operational use. Missing required indicators should block computation; optional missing indicators may be skipped only with explicit flags.

Optional missing indicators are flagged and available weights are renormalized so missing optional data do not mechanically lower scores. The framework separates `data_quality_flag` from `model_completeness_flag` to distinguish row-level input gaps from model-configuration completeness.

Feasibility is not the same as need. The cash model separates `cash_need_score`, `cash_feasibility_score`, and `cash_priority` so delivery feasibility is reported as a component and warning rather than silently suppressing humanitarian need.

Priority scores remain decision-support indices. They are not confirmed damage estimates, beneficiary lists, dispatch orders, or official allocation rules. Every score should be interpreted with data-quality flags, model-completeness flags, uncertainty notes, and local validation.
