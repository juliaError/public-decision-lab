# Adapter Contract

## Purpose

Adapters connect external or local data sources to the stable local-file pipeline. The core pipeline should continue to consume standardized local files. Adapters are responsible for preparing those local artifacts and documenting provenance, limitations, and update behavior.

This contract is intentionally conservative. It supports local-file adapters for selected future sources, but it does not add NASA LANCE, Copernicus GFM, GDACS, WorldPop download, Overpass, or satellite-processing API logic yet.

## Core Principle

Adapters should return:

- a local path;
- a layer name;
- metadata describing the source, terms, limitations, and whether anything was automatically downloaded.

Adapters should not:

- make official claims;
- change exposure results directly;
- hide source limitations;
- commit large data;
- expose private or sensitive data;
- silently call remote APIs in tests.

## Current Types

### `DisasterEvent`

`DisasterEvent` is a minimal event metadata object with:

- `event_id`;
- `hazard_type`;
- `name`;
- `source`;
- optional UTC start/end time;
- optional description;
- free-form string metadata.

Future GDACS or similar event adapters should return `DisasterEvent` objects before running the exposure pipeline.

### `AdapterMetadata`

Every adapter result should include:

- source name;
- source URL when available;
- license or terms when available;
- spatial resolution;
- temporal resolution;
- update frequency;
- source type;
- whether data are observed, modeled, crowdsourced, manually supplied, or mixed;
- known limitations;
- whether the adapter automatically downloaded data;
- notes.

### `AdapterResult`

`AdapterResult` includes:

- `path`: local standardized artifact;
- `layer_name`: intended pipeline layer name, such as `hazard`;
- `metadata`: adapter provenance and limitations.

## Current Local Adapter

`LocalHazardAdapter` wraps an existing local hazard GeoJSON file and validates that it can be loaded as a hazard polygon layer. It does not download data or certify that the hazard file is authoritative.

`LocalNasaLanceFloodAdapter` accepts an existing local NASA LANCE-style flood raster GeoTIFF, thresholds flood pixels, and writes a local hazard GeoJSON. It does not download NASA LANCE data and does not validate product timing, CRS, or class semantics.

`LocalCopernicusGFMFloodAdapter` accepts an existing local Copernicus GFM-style flood raster GeoTIFF, thresholds flood pixels, and writes a local hazard GeoJSON. It does not download Copernicus GFM data and does not validate product timing, CRS, or class semantics.

`LocalGdacsEventAdapter` reads a local GDACS-style JSON event manifest and returns `DisasterEvent` objects. It does not poll GDACS feeds, choose AOIs, or trigger the exposure pipeline automatically.

Example:

```python
from disaster_nowcaster.adapters import LocalHazardAdapter

adapter = LocalHazardAdapter(
    "examples/sample_flood_extent.geojson",
    hazard_type="flood",
)
result = adapter.prepare()
print(result.path)
print(result.metadata.to_dict())
```

Local raster hazard preparation can also be run from the CLI:

```bash
disaster-nowcaster prepare-hazard nasa-lance-local \
  --raster local_flood.tif \
  --output prepared_hazard.geojson \
  --flood-value 1

disaster-nowcaster prepare-hazard copernicus-gfm-local \
  --raster local_gfm_flood.tif \
  --output prepared_hazard.geojson \
  --flood-value 1
```

## Future Adapter Roadmap

### NASA LANCE Flood Product

Future work can add a NASA LANCE adapter that downloads or reads flood GeoTIFF products and converts them into the local hazard input expected by the pipeline. The first safe step should support local user-supplied NASA-style GeoTIFF files before automatic download.

Current implementation status: local user-supplied NASA-style GeoTIFF files are supported through `LocalNasaLanceFloodAdapter`; automatic download remains future work.

### Copernicus GFM

Future work can add a Copernicus GFM network adapter after the product interface and data formats are documented. It should emit a local hazard layer and metadata, not bypass the core pipeline.

Current implementation status: local user-supplied Copernicus GFM-style GeoTIFF files are supported through `LocalCopernicusGFMFloodAdapter`; automatic download remains future work.

### GDACS Event Trigger

Future work can add a GDACS network adapter that lists events and builds `DisasterEvent` objects. A separate orchestrator can then decide which hazard adapter to use.

Current implementation status: local GDACS-style JSON manifests are supported through `LocalGdacsEventAdapter`; live feed polling remains future work.

### Cloud Automation

The first cloud workflow is a manually triggered GitHub Actions demo that runs the static sample inputs and uploads output artifacts. Future event-triggered cloud automation is described in `docs/cloud_automation.md`.

## Testing Rules

Adapter unit tests should:

- use tiny synthetic local fixtures;
- avoid network access;
- avoid real disaster data;
- check metadata and limitations;
- check that local artifacts can be loaded by the core pipeline.

## Interpretation

Adapter outputs are inputs for exposure screening. They do not imply confirmed damage, verified victims, official priorities, or validated disaster impacts.
