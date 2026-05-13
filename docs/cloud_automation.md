# Cloud Automation Plan

## Purpose

This document describes how Disaster Impact Nowcaster can move from a local static demo to a cloud-runnable nowcasting prototype. The v0.1 cloud path is intentionally conservative: it runs the existing synthetic/sample demo in GitHub Actions and stores outputs as a workflow artifact. It does not poll live disaster feeds, download satellite data, or publish official results.

All automated outputs must remain clearly labeled as decision-support exposure screening:

- estimated exposed population, not confirmed affected people;
- potentially affected infrastructure, not verified damage or service disruption;
- priority scores for review, not official allocation rules;
- requires validation against authoritative sources and local knowledge.

## v0.1 Cloud Demo

The first cloud workflow is `.github/workflows/cloud-demo.yml`.

It can be run manually with GitHub Actions `workflow_dispatch`. The job:

1. checks out the repository;
2. installs the package;
3. runs the static sample demo with local files in `examples/`;
4. checks that expected output files exist;
5. uploads `outputs/demo_event/` as a workflow artifact.

This proves that a person does not need to run the demo on their own machine once the repository is pushed to GitHub. It does not prove live nowcasting.

## Future Cloud Architecture

The production-oriented flow should be:

```text
GDACS event polling or manual event manifest
    ↓
Event registry and duplicate check
    ↓
AOI and time-window selection
    ↓
Hazard adapter selection
    ↓
Local standardized hazard, population, roads, facilities, and admin inputs
    ↓
disaster-nowcaster run
    ↓
Output artifact storage
    ↓
Validation gate
    ↓
Optional publication or notification
```

### 1. Event Trigger Layer

GDACS is the natural first trigger source because it provides global disaster alert information. The current repository only includes `LocalGdacsEventAdapter`, which reads a local JSON manifest and creates `DisasterEvent` objects. A future network adapter can poll GDACS feeds and write the same manifest format before triggering a run.

The trigger layer should maintain an event registry with:

- event ID;
- hazard type;
- event name;
- source;
- first-seen time;
- last-run time;
- output artifact location;
- validation status.

This prevents duplicate runs and keeps automated outputs auditable.

### 2. Hazard Preparation Layer

The current local adapters prepare hazard GeoJSON from user-supplied raster or vector files:

- `LocalHazardAdapter` for existing local hazard GeoJSON;
- `LocalNasaLanceFloodAdapter` for local NASA LANCE-style flood GeoTIFF;
- `LocalCopernicusGFMFloodAdapter` for local Copernicus GFM-style flood GeoTIFF.

Future network adapters should still emit local standardized files and metadata. They should not bypass the core CLI pipeline.

### 3. Execution Layer

For v0.1, GitHub Actions is the simplest execution platform:

- `workflow_dispatch` gives a manual cloud run button;
- workflow artifacts store generated reports, maps, CSVs, and metadata;
- no cloud credentials are required for the sample demo.

For a production prototype, stronger options are:

- GitHub Actions scheduled workflow for low-frequency polling and public demo outputs;
- AWS EventBridge Scheduler plus ECS/Fargate or AWS Batch for containerized event runs;
- Google Cloud Scheduler or Workflows plus Cloud Run Jobs for containerized event runs;
- Azure Container Apps Jobs or Functions for scheduled container execution.

The execution environment should run the same command used locally:

```bash
disaster-nowcaster run \
  --aoi <local-aoi.geojson> \
  --hazard <local-hazard.geojson> \
  --roads <local-roads.geojson> \
  --facilities <local-facilities.geojson> \
  --admin <local-admin.geojson> \
  --population <local-population.tif> \
  --output <event-output-dir>
```

### 4. Storage And Publication

Generated outputs should be written to event-specific folders. In a cloud system, that folder can be uploaded to object storage such as S3, Google Cloud Storage, Azure Blob Storage, or a GitHub Actions artifact.

Do not publish outputs automatically until validation rules are defined. A safer early pattern is:

1. run automatically;
2. save outputs privately or as restricted artifacts;
3. notify reviewers;
4. publish only after manual validation.

### 5. Validation Gate

Before any public use, reviewers should check:

- whether the event trigger matches the hazard and AOI;
- whether hazard timing matches the event window;
- whether raster/vector CRS and units are compatible;
- whether population, roads, and facilities data are current enough for the use case;
- whether outputs distinguish exposure from confirmed damage;
- whether sensitive facilities or locations require masking.

### 6. Security And Privacy

The cloud runner should:

- use least-privilege credentials;
- avoid committing API keys or tokens;
- store secrets only in the cloud platform secret manager;
- avoid individual-level data;
- log inputs, code version, and output paths;
- keep raw external data outside the repository.

## Adapter Roadmap

### GDACS

Current status: local manifest adapter only.

Future work:

- poll a GDACS feed;
- normalize alerts into `DisasterEvent`;
- filter by hazard type, severity, geography, and update time;
- trigger a run only after duplicate checks.

### NASA LANCE

Current status: local GeoTIFF adapter only.

Future work:

- discover candidate flood products for an event window;
- download to cloud object storage or a temporary working directory;
- verify product class semantics and timing;
- pass the local raster to `LocalNasaLanceFloodAdapter` or a network adapter with the same output contract.

### Copernicus GFM

Current status: local raster adapter only.

Future work:

- evaluate official GFM access channels and product formats;
- download or request event-specific observed flood extent products;
- preserve product metadata and quality notes;
- convert to the standardized hazard GeoJSON used by the core pipeline.

## Official Reference Starting Points

These links should be re-checked when implementing live network adapters:

- [NASA Earthdata NRT Global Flood Products](https://www.earthdata.nasa.gov/data/instruments/viirs/near-real-time-data/nrt-global-flood-products)
- [NASA LANCE FLOOD viewer](https://lance.modaps.eosdis.nasa.gov/flood/)
- [Copernicus GloFAS data and services, including GFM access channels](https://global-flood.emergency.copernicus.eu/general-information/data-and-services/)
- [Copernicus GFM product launch overview](https://global-flood.emergency.copernicus.eu/news/107-global-flood-monitoring-product-launch/)
- [GDACS alerts feed](https://gdacs.org/Default.aspx/Alerts/xml/rss.xml)
- [GitHub Docs: manually running a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)
- [GitHub Docs: workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts)

## Non-Goals For v0.1

- No live GDACS polling.
- No automatic NASA LANCE download.
- No automatic Copernicus GFM download.
- No public publication workflow.
- No official allocation decision.
- No confirmed damage claim.
