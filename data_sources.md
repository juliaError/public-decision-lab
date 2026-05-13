# Data Sources

The first skeleton does not connect to external data sources.

## Current Inputs

Users provide local GeoJSON files for:

- AOI polygon;
- hazard polygon;
- administrative boundaries;
- road lines;
- facility points.
- optional population raster GeoTIFF.

Local raster hazard adapters can also prepare a hazard GeoJSON from user-supplied flood GeoTIFF files.

## Example Files

Files in `examples/` and `tests/fixtures/` are tiny synthetic files used only to demonstrate and test the workflow. They are not real disaster observations or real WorldPop data and should not be interpreted as evidence about any place or event.

## WorldPop

WorldPop provides open high-resolution population-distribution products that can be used for population exposure estimates after a user downloads the relevant raster. This project currently accepts only local GeoTIFF input through `--population`; it does not automatically download WorldPop data.

## OpenStreetMap / HOT Export Tool

OpenStreetMap data can provide roads and facility points or polygons for exposure screening. The HOT Export Tool is a practical way to create local extracts for humanitarian analysis, including roads, hospitals, clinics, schools, shelters, buildings, and other mapped features.

Current support:

- local GeoJSON files;
- local GeoPackage files;
- road line features;
- facility point or polygon features with supported types: `hospital`, `clinic`, `school`, `shelter`.

Common supported OSM tags include:

- `amenity=hospital`;
- `amenity=clinic`;
- `amenity=school`;
- `amenity=shelter`;
- `healthcare=hospital`;
- `healthcare=clinic`;
- project-provided `facility_type=hospital|clinic|school|shelter`.

Limitations:

- The project does not call Overpass API or automatically download OSM data yet.
- OSM completeness varies by place and feature type.
- Facilities inside a hazard extent are potentially exposed, not confirmed damaged or nonfunctional.
- Road length is measured in the input CRS units; use a suitable projected CRS for meter-like lengths.
- Local GeoJSON or GeoPackage layers must already align with the AOI, hazard, and admin-unit CRS.

## Future Source Documentation

Every future adapter should document:

- source name;
- source URL or citation, where available;
- license or terms of use;
- spatial resolution;
- temporal resolution;
- update frequency;
- known limitations;
- whether the data are observed, modeled, crowdsourced, or manually supplied.

Adapter metadata fields are defined in `docs/adapter_contract.md`. The current adapter implementation is local-only and does not automatically download external disaster data.

## NASA LANCE-Style Local Flood Raster

NASA LANCE provides near-real-time Earth observation products, including flood-related products. The current implementation only supports local user-supplied NASA LANCE-style flood GeoTIFF files through `LocalNasaLanceFloodAdapter`.

Current support:

- local GeoTIFF input;
- configurable flood-value threshold;
- local hazard GeoJSON output.

Limitations:

- The adapter does not download NASA LANCE data.
- The adapter does not verify NASA product class semantics, timing, confidence, cloud effects, or validation status.
- No reprojection is performed.
- Output is a hazard input for exposure screening, not confirmed damage.

## Copernicus GFM-Style Local Flood Raster

Copernicus Global Flood Monitoring (GFM) is part of the Copernicus Emergency Management Service flood monitoring ecosystem. The current implementation only supports local user-supplied Copernicus GFM-style flood GeoTIFF files through `LocalCopernicusGFMFloodAdapter`.

Current support:

- local GeoTIFF input;
- configurable flood-value threshold;
- local hazard GeoJSON output.

Limitations:

- The adapter does not download Copernicus GFM data.
- The adapter does not verify GFM product class semantics, timing, quality flags, exclusion masks, or validation status.
- No reprojection is performed.
- Output is a hazard input for exposure screening, not confirmed damage.

## GDACS-Style Local Event Manifest

GDACS provides global disaster alert information that can eventually trigger event-specific runs. The current implementation only supports local GDACS-style JSON manifests through `LocalGdacsEventAdapter`.

Current support:

- local JSON manifest input;
- event records with `event_id` or `id`, `hazard_type` or `event_type`, and `name` or `title`;
- output as internal `DisasterEvent` objects.

Limitations:

- The adapter does not poll GDACS feeds.
- It does not choose an AOI, select a hazard product, or trigger a run automatically.
- Event metadata are triggers for review, not confirmed damage or verified local impacts.

## Cloud Automation Source Notes

The first GitHub Actions cloud demo uses only synthetic/sample repository inputs. Future live cloud automation should re-check official source documentation before implementing network adapters, store raw external data outside the repository, and preserve source metadata in event output folders.
