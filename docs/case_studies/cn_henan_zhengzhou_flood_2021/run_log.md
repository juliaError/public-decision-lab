# cn_henan_zhengzhou_flood_2021 Run Log

## Current Run Status

No nowcaster exposure run has been completed for this case yet.

Reason: no trustworthy flood polygon or clearly documented proxy hazard layer has been prepared. The case is intentionally marked `data_gap` rather than using a fabricated flood extent.

## Planned Run Stages

| Stage | Data cut-off | Status | Output path | Notes |
| --- | --- | --- | --- | --- |
| T0_baseline | 2021-07-16T23:59:59+08:00 | planned |  | Baseline data inventory only; the current CLI still requires a hazard layer. |
| T1_early_hazard | 2021-07-20T23:59:59+08:00 | data_gap |  | Needs event-time hazard or a clearly labeled proxy. |
| T2_updated_hazard | 2021-07-23T23:59:59+08:00 | data_gap |  | Needs updated hazard or observed extent source. |
| T3_diagnostic | 2022-01-21T23:59:59+08:00 | source_review |  | Post-event evidence can diagnose errors only. |

## Future Command Template

```bash
disaster-nowcaster run \
  --aoi <path-to-zhengzhou-aoi.geojson> \
  --hazard <path-to-verified-or-proxy-hazard.geojson> \
  --roads <path-to-roads.geojson> \
  --facilities <path-to-facilities.geojson> \
  --admin <path-to-admin-units.geojson> \
  --population <path-to-population.tif> \
  --output outputs/cn_henan_zhengzhou_flood_2021/<run_id>
```

## Required Output Check

When a run becomes possible, check that the output folder includes:

- `report.md`
- `impact_summary.csv`
- `priority_areas.csv`
- `affected_facilities.geojson`
- `affected_roads.geojson`
- `map.html`
- `metadata.json`
