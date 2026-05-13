# Adapter Contract

## Purpose

Adapters connect external or local data sources to the stable local-file pipeline. The core pipeline should continue to consume standardized local files. Adapters are responsible for preparing those local artifacts and documenting provenance, limitations, and update behavior.

This contract is intentionally conservative. It does not add NASA LANCE, Copernicus GFM, GDACS, WorldPop download, Overpass, or satellite-processing logic yet.

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

## Future Adapter Roadmap

### NASA LANCE Flood Product

Future work can add a NASA LANCE adapter that downloads or reads flood GeoTIFF products and converts them into the local hazard input expected by the pipeline. The first safe step should support local user-supplied NASA-style GeoTIFF files before automatic download.

### Copernicus GFM

Future work can add a Copernicus GFM adapter after the product interface and data formats are documented. It should emit a local hazard layer and metadata, not bypass the core pipeline.

### GDACS Event Trigger

Future work can add a GDACS event adapter that lists events and builds `DisasterEvent` objects. A separate orchestrator can then decide which hazard adapter to use.

## Testing Rules

Adapter unit tests should:

- use tiny synthetic local fixtures;
- avoid network access;
- avoid real disaster data;
- check metadata and limitations;
- check that local artifacts can be loaded by the core pipeline.

## Interpretation

Adapter outputs are inputs for exposure screening. They do not imply confirmed damage, verified victims, official priorities, or validated disaster impacts.
