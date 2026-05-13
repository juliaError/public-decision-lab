# pk_sindh_khairpur_flood_2022 Case Note

## Case Summary

This case focuses on the 2022 Pakistan floods around Khairpur Nathan Shah / Sindh Province, using public UNOSAT/HDX materials for the satellite-detected water extent observed from Sentinel-2 imagery acquired on 2022-08-31 and published shortly afterward.

The case was selected as the next iteration after the Zhengzhou case reached a reliable-hazard-layer data gap. Unlike Zhengzhou, this Pakistan case has an identifiable machine-readable UNOSAT flood-water vector package, plus a small district-level UNOSAT exposure workbook for diagnostic comparison.

## Evaluation Purpose

This case is intended to test whether Disaster Impact Nowcaster can:

- ingest an authoritative external flood-water product after local conversion;
- summarize potentially exposed roads and facilities;
- produce admin-level review outputs for a localized flood context;
- compare its outputs against UNOSAT district-level exposure summaries without claiming field validation;
- keep large external data out of the repository while preserving reproducibility.

## Current Data Status

Status: `source_review`

Prepared in repository:

- case manifest;
- source inventory;
- run-stage design;
- output-checking tooling;
- validation/evaluation template.

Not prepared in repository:

- local AOI GeoJSON;
- converted flood-water GeoJSON from the UNOSAT zipped shapefile;
- local admin boundaries matching the UNOSAT exposure workbook;
- local OSM roads and facilities extracts;
- local population raster.

## Why The Case Is Not Yet Claimed As A Completed Run

The UNOSAT zipped shapefile is approximately 286 MB. It should be downloaded to `data/external/` or cloud object storage, extracted, and converted outside the repository. A direct download attempt on 2026-05-14 was stopped because the connection was too slow for the current interactive session. The small UNOSAT exposure workbook was downloaded to `/private/tmp` and inspected only as diagnostic context.

This is a useful iteration because it identifies a concrete, public, machine-readable hazard input and the exact preprocessing step that must come next. It is not yet a completed historical case run.

## Non-Claims

- The system has not validated damage in Khairpur Nathan Shah.
- The system has not identified victims, confirmed losses, or official rescue priorities.
- UNOSAT preliminary flood-water outputs are not field-validated damage assessments.
- The UNOSAT exposure workbook is not a WorldPop raster input for the v0.1 pipeline.

## Next Concrete Step

Download the UNOSAT shapefile package outside the repository, extract the flood-water polygon layer, convert it to:

```text
data/external/pk_sindh_khairpur_flood_2022/hazard/unosat_khairpur_31aug2022_floodwater.geojson
```

Then prepare AOI, admin, roads, and facilities files in the same external case directory and run the v0.1 CLI.
