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
