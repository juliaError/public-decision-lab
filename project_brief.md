# Project Brief: Disaster Impact Nowcaster

## 1. One-Line Definition

**Disaster Impact Nowcaster** is a lightweight, open-source, reproducible disaster-impact nowcasting and action-priority layer that turns existing hazard data, exposure data, infrastructure data, and field reports into transparent impact summaries, priority rankings, maps, and machine-readable outputs.

In short:

> This project does **not** reinvent disaster forecasting or disaster mapping. It translates existing disaster information into reproducible, decision-relevant impact and priority outputs.

---

## 2. What This Project Does Not Do

This project is deliberately scoped as an **integration, exposure-estimation, and prioritization layer**, not as a replacement for authoritative disaster systems.

It does **not** aim to:

1. **Predict floods, earthquakes, tropical cyclones, wildfires, or other hazards from scratch.**
   - The project will rely on existing hazard forecasts, observed hazard layers, or externally produced disaster products.

2. **Replace official emergency management agencies or humanitarian response systems.**
   - Outputs are intended to support analysis, triage, research, and reproducible situational awareness, not to serve as official declarations of damage or need.

3. **Produce authoritative damage assessments.**
   - The project estimates exposure and potential impact. It does not confirm destruction, casualties, individual needs, or legal damage claims.

4. **Compete with authoritative satellite rapid-mapping services.**
   - It will not attempt to replace Copernicus EMS, UNOSAT, NASA, national mapping agencies, or other professional rapid-mapping teams.

5. **Build a new hydrological, meteorological, or seismic model.**
   - It will use external products such as flood extents, flood forecasts, ShakeMaps, cyclone tracks, fire detections, or other hazard layers.

6. **Track individuals or expose personally identifiable information.**
   - Future field-report or mobility modules must use aggregation, consent, minimization, and privacy-preserving design.

7. **Make fully automated life-and-death allocation decisions.**
   - Priority scores are decision-support outputs, not binding allocation rules. Human review, local knowledge, and institutional accountability remain necessary.

8. **Hide uncertainty behind precise-looking numbers.**
   - Every output should distinguish estimated exposure from confirmed impact and should report data limitations.

---

## 3. Relationship to Existing Systems

Disaster Impact Nowcaster is designed to sit **above** existing disaster-data systems as a thin, transparent, reproducible decision-support layer.

### 3.1 GDACS

**GDACS** provides global disaster alerts and event information for earthquakes, floods, tropical cyclones, volcanoes, and other hazards.

**This project’s role:**

- Use GDACS as an **event trigger** or event metadata source.
- Convert a disaster alert into an internal `DisasterEvent` object.
- Use the event to define an area of interest, time window, and relevant hazard type.

**This project does not:**

- Replace GDACS alerts.
- Re-score global disaster severity from scratch.

---

### 3.2 Copernicus Global Flood Monitoring / Copernicus EMS

**Copernicus GFM** and **Copernicus EMS Rapid Mapping** provide flood monitoring and rapid geospatial mapping products based on satellite imagery and other data.

**This project’s role:**

- Use Copernicus flood or rapid-mapping products as hazard inputs.
- Convert flood or damage layers into exposure estimates and priority outputs.
- Add reproducible summaries, tables, and action-relevant rankings.

**This project does not:**

- Replace Copernicus flood mapping.
- Claim to produce official Copernicus-equivalent rapid maps.

---

### 3.3 NASA LANCE / NASA Disaster Data Products

**NASA LANCE** and related NASA disaster-data systems provide near-real-time Earth observation products, including flood, fire, and other disaster-relevant layers.

**This project’s role:**

- Use NASA near-real-time products as optional hazard or monitoring inputs.
- Transform those layers into local exposure summaries and reports.

**This project does not:**

- Replace NASA near-real-time data services.
- Reprocess all raw satellite imagery from scratch in the initial versions.

---

### 3.4 UNOSAT

**UNOSAT** provides satellite imagery analysis and rapid mapping for humanitarian and disaster-response contexts.

**This project’s role:**

- Treat UNOSAT outputs, where publicly available, as high-quality validation or comparison layers.
- Learn from UNOSAT’s clear distinction between preliminary satellite-derived estimates and field-validated assessments.

**This project does not:**

- Replace professional UNOSAT rapid mapping.
- Present automated outputs as equivalent to expert-validated humanitarian mapping.

---

### 3.5 Google FloodHub / Google Flood Forecasting

**Google FloodHub** provides riverine flood forecasting and flood-risk alerts across many countries.

**This project’s role:**

- Use flood forecasts, where accessible, as one possible hazard input.
- Translate forecasts into population exposure, infrastructure exposure, and preparedness-priority outputs.

**This project does not:**

- Build a new global hydrological forecasting model.
- Compete with Google’s flood forecasting infrastructure.

---

### 3.6 InaSAFE

**InaSAFE** is a QGIS-oriented tool for estimating impacts of natural hazards on people and infrastructure.

**This project’s role:**

- Share the broad goal of turning hazard and exposure layers into impact estimates.
- Differ by emphasizing a lightweight, cloud-friendly, CLI/API-first, reproducible workflow suitable for automated reports and integration with multiple data ports.

**This project does not:**

- Replace QGIS-based desktop disaster-impact analysis.
- Reimplement every InaSAFE capability.

---

### 3.7 CLIMADA

**CLIMADA** is a comprehensive open-source framework for climate risk and adaptation assessment, combining hazards, exposure, vulnerability, and impact functions.

**This project’s role:**

- Potentially use CLIMADA as an optional backend for advanced risk modeling.
- Focus instead on a lighter operational layer for event-specific nowcasting, reporting, and prioritization.

**This project does not:**

- Replace CLIMADA’s scientific climate-risk modeling framework.
- Attempt to cover all climate-risk and adaptation-analysis use cases.

---

### 3.8 OpenQuake

**OpenQuake** is a professional open-source engine for seismic hazard and risk modeling.

**This project’s role:**

- Use USGS ShakeMap or OpenQuake outputs as earthquake hazard/risk inputs.
- Convert earthquake intensity or risk layers into exposure summaries and response-priority outputs.

**This project does not:**

- Build a new seismic hazard model.
- Replace OpenQuake for earthquake risk analysis.

---

### 3.9 Ushahidi

**Ushahidi** is an open-source platform for crowdsourced crisis reporting and mapping.

**This project’s role:**

- Potentially ingest field reports from Ushahidi, KoBoToolbox, RapidPro, Sahana, or similar tools.
- Use reports as one input into validation, needs mapping, and priority scoring.

**This project does not:**

- Build a new crowdsourcing social platform.
- Publicly expose sensitive individual reports by default.

---

## 4. First-Version MVP Scope

The first MVP should be intentionally narrow.

### 4.1 MVP Name

**v0.1: Static Flood Exposure and Priority Report**

### 4.2 MVP Goal

Given a hazard layer and exposure layers for a specific area, generate a reproducible disaster-impact report.

### 4.3 MVP Hazard Type

Initial hazard focus:

- **Flood exposure**

The first version should **not** automatically download or classify satellite imagery. It should accept an existing flood extent or hazard layer as input.

### 4.4 MVP Inputs

The MVP should accept local files:

1. Area of interest polygon
2. Flood or hazard extent polygon/raster
3. Administrative boundaries
4. Population raster or population grid
5. Roads layer
6. Facilities layer, including at least:
   - hospitals
   - clinics
   - schools
   - shelters, if available

### 4.5 MVP Outputs

The MVP should generate:

1. `impact_summary.csv`
2. `priority_areas.csv`
3. `affected_roads.geojson`
4. `affected_facilities.geojson`
5. `map.html`
6. `report.md`
7. `metadata.json`
8. `uncertainty_note.md`

### 4.6 MVP Command-Line Interface

A first working command should look like:

```bash
disaster-nowcaster run \
  --aoi examples/sample_aoi.geojson \
  --hazard examples/sample_flood_extent.geojson \
  --admin examples/sample_admin_units.geojson \
  --population examples/sample_population.tif \
  --roads examples/sample_roads.geojson \
  --facilities examples/sample_facilities.geojson \
  --output outputs/demo_event
```

### 4.7 MVP Success Criterion

The MVP is successful if a user can run one documented command and obtain:

- a reproducible exposure table;
- a ranked list of priority areas;
- a static HTML map;
- a one-page Markdown report;
- a clear uncertainty statement;
- metadata documenting all input sources and assumptions.

---

## 5. Target Users

The project is designed for users who need transparent, reproducible disaster-impact estimates but may not have access to large institutional disaster-analysis systems.

### 5.1 Primary Users

1. **Researchers**
   - Economists, geographers, public-policy researchers, disaster-risk researchers, climate-risk researchers.

2. **Humanitarian analysts**
   - Analysts at NGOs, civil-society organizations, student groups, and small response teams.

3. **Public agencies and local governments**
   - Users who need reproducible situational awareness and prioritization support.

4. **Open-source civic-technology contributors**
   - Developers interested in public-risk monitoring and humanitarian data infrastructure.

5. **Journalists and investigative researchers**
   - Users who need transparent exposure summaries and data provenance.

6. **Students and educators**
   - Users learning disaster-data analysis, geospatial workflows, and public-interest software engineering.

### 5.2 Non-Target Users for Early Versions

The early versions are not designed for:

- real-time emergency dispatch without human verification;
- official damage certification;
- individual rescue triage;
- personally identifiable missing-person management;
- classified or sensitive operational use.

---

## 6. Input Data

The project should treat all inputs as explicit, documented, and replaceable.

### 6.1 Event Inputs

Possible event sources:

- manual event definition;
- GDACS event feed;
- USGS earthquake event feed;
- cyclone track products;
- flood alert or forecast products.

Initial MVP:

- manual event metadata.

### 6.2 Hazard Inputs

Possible hazard inputs:

- flood extent polygon;
- flood extent raster;
- Copernicus GFM products;
- NASA LANCE flood products;
- Google FloodHub or other flood-forecast layers;
- USGS ShakeMap for earthquakes;
- NASA FIRMS for wildfire hot spots;
- cyclone wind/rainfall/flood layers.

Initial MVP:

- local flood extent GeoJSON or GeoTIFF.

### 6.3 Exposure Inputs

Exposure layers may include:

- population rasters or grids;
- buildings;
- roads;
- bridges;
- hospitals;
- clinics;
- schools;
- shelters;
- power infrastructure;
- water infrastructure;
- administrative boundaries;
- poverty or vulnerability proxies.

Initial MVP:

- population raster;
- roads GeoJSON or GeoPackage;
- facilities GeoJSON or GeoPackage;
- administrative boundaries.

### 6.4 Field-Report Inputs

Future optional inputs may include:

- web forms;
- KoBoToolbox submissions;
- RapidPro / SMS data;
- Ushahidi reports;
- Sahana or other humanitarian information-management systems;
- aggregated mobile-mobility indicators, subject to strict privacy constraints.

Initial MVP:

- no live field-report ingestion.

### 6.5 Metadata Requirements

Every input dataset should record:

- source name;
- source URL or citation, if available;
- license or terms of use;
- spatial resolution;
- temporal resolution;
- acquisition or update time;
- processing date;
- known limitations;
- whether the data are observed, modeled, crowdsourced, or manually supplied.

---

## 7. Outputs

The project should produce outputs that are useful to both humans and machines.

### 7.1 Human-Readable Outputs

1. **Markdown impact report**
   - Event summary
   - Input data summary
   - Estimated exposed population
   - Potentially affected infrastructure
   - Top-ranked priority areas
   - Map links
   - Uncertainty note
   - Validation checklist

2. **Static HTML map**
   - AOI layer
   - Hazard layer
   - Administrative boundaries
   - Affected facilities
   - Affected roads
   - Priority areas, if available

3. **Uncertainty note**
   - Clear distinction between exposure and confirmed damage
   - Known sources of overestimation or underestimation
   - Data gaps
   - Suggested validation steps

### 7.2 Machine-Readable Outputs

1. `impact_summary.csv`
2. `priority_areas.csv`
3. `affected_roads.geojson`
4. `affected_facilities.geojson`
5. `metadata.json`
6. Optional future outputs:
   - GeoPackage
   - Cloud-Optimized GeoTIFF
   - PMTiles
   - STAC item metadata
   - API JSON response

### 7.3 Report Language

Initial reports should be generated in English. Future versions may support multilingual report templates.

---

## 8. Methodological Principles

### 8.1 Exposure First, Damage Later

The project estimates **exposure** before claiming **damage**.

- Exposure means a population, road, building, school, hospital, or other asset overlaps with a hazard area or falls inside a hazard-intensity zone.
- Damage means verified physical destruction, service disruption, injury, death, loss, or other confirmed consequences.

The default wording should be:

- “estimated exposed population”
- “potentially affected roads”
- “facilities located within the hazard extent”

Avoid default wording such as:

- “confirmed victims”
- “destroyed hospitals”
- “actual losses”

unless independently verified data support those claims.

### 8.2 Transparent Prioritization

Priority scores should be simple, documented, and configurable.

A first priority-score structure may be:

```text
priority_score_i =
    w1 * normalized_exposed_population_i
  + w2 * normalized_affected_facilities_i
  + w3 * normalized_road_disruption_i
  + w4 * normalized_vulnerability_proxy_i
```

Requirements:

- weights must be user-configurable;
- all input indicators must be reported;
- ranks must be reproducible;
- no score should be presented as an official allocation rule;
- sensitivity checks should be possible when weights change.

### 8.3 Modularity

The project should be organized around replaceable modules:

- event adapters;
- hazard adapters;
- exposure adapters;
- field-report adapters;
- scoring modules;
- report generators;
- validation modules.

No single data source should be hard-coded as the only acceptable input.

### 8.4 Reproducibility

Every output should be reproducible from:

- input files;
- configuration files;
- software version;
- processing timestamp;
- documented assumptions.

The project should prefer:

- deterministic workflows;
- explicit configuration files;
- small test fixtures;
- automated tests;
- versioned outputs.

### 8.5 Human Review

The system should be designed for decision support, not autonomous action.

Every report should include a validation checklist, such as:

- compare with official reports;
- compare with local field reports;
- check whether flood detection may miss built-up areas;
- check whether population data are outdated;
- check whether roads or facilities are missing from OpenStreetMap;
- check whether administrative boundaries match local definitions.

### 8.6 Avoid False Precision

The project should avoid overly precise language when data quality does not support it.

For example:

- Prefer “approximately 12,000 people are estimated to be exposed” over “12,037 people are affected.”
- Prefer “potentially affected” over “damaged” unless damage is validated.

### 8.7 Extensibility Across Hazards

Although the first MVP focuses on floods, the architecture should support future modules for:

- earthquakes;
- tropical cyclones;
- wildfires;
- heat waves;
- droughts;
- landslides;
- compound disasters.

---

## 9. Uncertainty and Ethics Principles

### 9.1 Uncertainty Principles

Every report must include an uncertainty section.

Minimum uncertainty dimensions:

1. **Hazard uncertainty**
   - satellite revisit gaps;
   - cloud cover for optical data;
   - SAR limitations in urban or vegetated areas;
   - model uncertainty in forecasts;
   - temporal mismatch between event timing and observation timing.

2. **Exposure uncertainty**
   - population data may be outdated;
   - roads and facilities may be incomplete in OpenStreetMap;
   - buildings may be missing or misclassified;
   - administrative boundaries may not match local operational units.

3. **Impact uncertainty**
   - exposure is not confirmed damage;
   - infrastructure inside a hazard zone may remain functional;
   - infrastructure outside the hazard zone may still be disrupted;
   - service disruptions may depend on network effects, staff availability, power, and supply chains.

4. **Prioritization uncertainty**
   - weights are normative choices;
   - different agencies may choose different objectives;
   - priority rankings should be stress-tested under alternative weights.

### 9.2 Ethical Principles

The project should follow these principles:

1. **Do no harm**
   - Do not expose vulnerable communities, sensitive facilities, or individual reports in ways that increase risk.

2. **Privacy by design**
   - Do not collect or publish personally identifiable information by default.
   - Any future field-report or survival-status module must apply consent, minimization, aggregation, access control, and deletion rules.

3. **No individual tracking**
   - Mobile-phone or mobility modules, if ever added, must use aggregated, privacy-preserving indicators only.

4. **Clear separation between public outputs and restricted data**
   - Some operational data may be too sensitive for public release.
   - Public reports should avoid exposing precise locations of vulnerable individuals or unprotected shelters when that could create harm.

5. **Local validation matters**
   - Automated outputs should not override local knowledge or field verification.

6. **Accountability**
   - Priority scores must be explainable.
   - Reports must show data sources and assumptions.
   - Users must be able to inspect how rankings were produced.

7. **Avoid techno-solutionism**
   - The project should support institutions and communities, not pretend that software alone solves disaster response.

---

## 10. Roadmap: v0.1 to v1.0

## v0.1 — Static Flood Exposure MVP

**Goal:** Produce a complete report from local files.

Core features:

- load AOI polygon;
- load flood extent polygon or raster;
- load administrative boundaries;
- load population raster;
- load roads and facilities;
- compute exposed population;
- compute affected road length;
- compute affected facility counts;
- aggregate outputs by administrative unit;
- generate `impact_summary.csv`;
- generate `priority_areas.csv`;
- generate `report.md`;
- generate `map.html`;
- write `metadata.json`;
- include uncertainty note;
- include automated tests with small synthetic fixtures.

Success criterion:

- A documented demo runs locally with one command and produces all required outputs.

---

## v0.2 — Data Source Adapters

**Goal:** Add controlled adapters for common open data sources.

Potential features:

- WorldPop local-download support;
- OpenStreetMap / HOT export ingestion;
- Copernicus GFM ingestion;
- NASA LANCE flood-product ingestion;
- simple configuration files for data paths and source metadata;
- stronger validation of coordinate reference systems and geometry validity.

Success criterion:

- A user can replace sample files with real-world open data and reproduce a flood exposure report.

---

## v0.3 — Event Trigger and Batch Processing

**Goal:** Move from one manual event to repeatable event processing.

Potential features:

- internal `DisasterEvent` schema;
- manual event YAML input;
- GDACS adapter;
- event-specific output folders;
- batch processing of multiple events;
- event metadata in all reports.

Success criterion:

- The system can process a list of events and produce one folder per event.

---

## v0.4 — Priority Scoring and Sensitivity Analysis

**Goal:** Strengthen the action-priority layer.

Potential features:

- configurable priority weights;
- alternative priority objectives;
- vulnerability proxies;
- road isolation measures;
- facility service-area exposure;
- sensitivity analysis under alternative weights;
- clearer reporting of normative assumptions.

Success criterion:

- Reports include both baseline priority rankings and sensitivity notes.

---

## v0.5 — Cloud and Automation Prototype

**Goal:** Make the workflow runnable in a low-cost cloud environment.

Potential features:

- GitHub Actions test workflow;
- optional scheduled demo workflow;
- Dockerfile;
- reproducible environment lock file;
- automated demo report generation;
- publication of demo outputs to GitHub Pages.

Success criterion:

- A public demo report and map can be automatically regenerated from the repository.

---

## v0.6 — Multi-Hazard Architecture

**Goal:** Generalize beyond floods while keeping the system modular.

Potential hazard adapters:

- earthquake: USGS ShakeMap / OpenQuake outputs;
- wildfire: NASA FIRMS hot spots and fire perimeters;
- tropical cyclone: cyclone tracks, wind, rainfall, and flood layers;
- heat: extreme heat exposure surfaces;
- drought: vegetation, precipitation, soil moisture, and food-security indicators.

Success criterion:

- At least one non-flood hazard can be processed through the same report and priority framework.

---

## v0.7 — Field Report Integration

**Goal:** Add optional non-sensitive field-report ingestion.

Potential features:

- ingest structured reports from CSV, KoBoToolbox, Ushahidi, RapidPro, or Sahana exports;
- classify reports by need type;
- aggregate reports to administrative units or grid cells;
- include field-report intensity in priority scores;
- flag conflicting or unverified reports.

Success criterion:

- Field reports can be incorporated without exposing personally identifiable information.

---

## v0.8 — Validation and Benchmarking

**Goal:** Compare automated outputs with external references.

Potential validation sources:

- official damage reports;
- Copernicus EMS maps;
- UNOSAT maps;
- local assessments;
- humanitarian situation reports;
- historical events with known outcomes.

Potential features:

- validation metrics;
- spatial overlap comparison;
- overestimation / underestimation diagnostics;
- validation report template.

Success criterion:

- Each case study includes at least one validation or plausibility check.

---

## v0.9 — Documentation and Case Studies

**Goal:** Make the project usable by external contributors.

Potential features:

- full documentation site;
- installation guide;
- tutorial notebooks;
- example case studies;
- contribution guide;
- data-source guide;
- ethics and safety guide;
- reproducibility checklist.

Success criterion:

- A new user can run a tutorial case without private assistance.

---

## v1.0 — Stable Public Release

**Goal:** Release a stable, documented, tested version of the toolkit.

Expected features:

- stable CLI;
- stable Python API;
- flood workflow with real open data;
- at least one additional hazard workflow or adapter;
- report and map generation;
- priority scoring with sensitivity analysis;
- metadata and uncertainty reporting;
- automated tests;
- reproducible demo;
- public documentation;
- citation metadata;
- clear license;
- example case studies.

Success criterion:

- The project can be used by researchers, analysts, and civic-technology contributors as a reproducible disaster-impact nowcasting and prioritization toolkit.

---

## Short Project Positioning Statement

Disaster Impact Nowcaster is not another disaster map. It is a lightweight integration and prioritization layer that helps users turn existing disaster hazard data, population data, infrastructure data, and field reports into reproducible, transparent, and action-relevant outputs.

Its core contribution is to move from:

```text
hazard layer → visual map
```

to:

```text
hazard layer + exposure + vulnerability + infrastructure + uncertainty
→ impact summary + priority ranking + map + report + metadata
```

The project’s long-run ambition is to provide a reusable open-source foundation for disaster-response analysis, humanitarian data workflows, public-risk monitoring, and welfare-oriented emergency prioritization.

