# pk_sindh_khairpur_flood_2022 Run Log

## Run Stages

| Stage | Data cut-off | Status | Output path | Notes |
| --- | --- | --- | --- | --- |
| T0_baseline | 2022-08-30T23:59:59+05:00 | planned | none yet | Baseline AOI/admin/infrastructure layers not prepared locally. |
| T1_early_hazard | 2022-09-02T23:59:59+05:00 | data_gap | none yet | Do not use response-plan affected districts as a flood polygon. |
| T2_updated_hazard | 2022-09-07T23:59:59+05:00 | source_review | none yet | UNOSAT vector source identified; local conversion still pending. |
| T3_diagnostic | 2022-09-20T23:59:59+05:00 | source_review | none yet | UNOSAT exposure workbook and situation reports can support diagnostic comparison only. |

## Local Data Attempt

On 2026-05-14, the public HDX CKAN API confirmed the UNOSAT Khairpur dataset and resources:

- zipped shapefile: `https://unosat.org/static/unosat_filesystem/3349/FL20220808PAK_SHP.zip`
- size: about 286 MB
- license: Creative Commons Attribution Share-Alike
- limitation: preliminary analysis, not field validated

A direct shapefile download to `/private/tmp` was started and then stopped because transfer speed was too slow for the interactive session. The partial file must not be used as an input.

The small UNOSAT exposure workbook was downloaded to `/private/tmp` and inspected for diagnostic context. The workbook reports district-level analyzed area, flood-water extent, total population in analyzed area, and potentially exposed population. Example rows include Dadu, Ghotki, Jacobabad, Kashmore, Khairpur, Larkana, Naushahro Feroze, Qambar Shahdadkot, Shikarpur, and Sukkur. These numbers are not reproduced as pipeline results because they come from UNOSAT's own analysis, not this tool.

## Planned Command After External Data Preparation

```bash
disaster-nowcaster run \
  --aoi data/external/pk_sindh_khairpur_flood_2022/aoi.geojson \
  --hazard data/external/pk_sindh_khairpur_flood_2022/hazard/unosat_khairpur_31aug2022_floodwater.geojson \
  --roads data/external/pk_sindh_khairpur_flood_2022/roads.geojson \
  --facilities data/external/pk_sindh_khairpur_flood_2022/facilities.geojson \
  --admin data/external/pk_sindh_khairpur_flood_2022/admin.geojson \
  --output outputs/pk_sindh_khairpur_flood_2022/t2_updated_hazard
```

If a local population raster is prepared later, add:

```bash
  --population data/external/pk_sindh_khairpur_flood_2022/population.tif
```

## Output Verification Command

After the run finishes:

```bash
disaster-nowcaster case check-outputs \
  --output outputs/pk_sindh_khairpur_flood_2022/t2_updated_hazard
```

The checker confirms only that the core files exist. It does not validate scientific quality, event interpretation, or response usefulness.
