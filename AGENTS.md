# AGENTS.md

## Project Identity

This repository implements **Disaster Impact Nowcaster**, a lightweight open-source toolkit for turning existing hazard layers, exposure data, infrastructure data, and field reports into reproducible impact summaries and action-priority lists.

This project belongs to **Civic Measurement Lab**.

The project is an **integration, exposure-estimation, reporting, and prioritization layer**. It does **not** aim to replace authoritative hazard forecasting, official disaster mapping, emergency management agencies, or humanitarian response systems.

The core positioning is:

> A lightweight, open-source, reproducible disaster-impact nowcasting and action-priority layer.

The project should translate existing disaster information into decision-relevant outputs:

- estimated exposed population;
- potentially affected roads and facilities;
- administrative-unit summaries;
- transparent priority rankings;
- reproducible maps and reports;
- metadata and uncertainty notes.

---

## Non-Negotiable Rules

These rules must be followed in every task, commit, and pull request.

### Data and Scientific Integrity

- Do **not** fabricate data.
- Do **not** fabricate scientific claims.
- Do **not** hard-code fake results.
- Do **not** present exposure estimates as confirmed damage.
- Do **not** present priority scores as official allocation decisions.
- Do **not** imply that the tool identifies confirmed victims, confirmed losses, or verified infrastructure destruction unless validated data explicitly support that claim.

Preferred language:

- “estimated exposed population”;
- “potentially affected roads”;
- “facilities located within the hazard extent”;
- “priority score for decision support.”

Avoid unsupported language:

- “confirmed victims”;
- “destroyed hospitals”;
- “actual losses”;
- “official rescue priority.”

### Privacy and Safety

- Do **not** commit API keys, tokens, credentials, passwords, private configuration files, or private data.
- Do **not** commit personally identifiable information.
- Do **not** implement individual tracking.
- Do **not** publish precise sensitive locations if doing so could increase risk.
- Future field-report or mobility modules must use aggregation, minimization, consent, and privacy-preserving design.

### Data Storage

- Do **not** commit large raw data files.
- Use small synthetic fixtures only for tests.
- Store large external data outside the repository.
- Provide download instructions or scripts instead of committing bulky datasets.
- If a sample file is needed, it must be small, synthetic, and clearly labeled as synthetic.

### Documentation Requirements

Every data source adapter must document:

- source name;
- source URL or citation, where available;
- license or terms of use;
- spatial resolution;
- temporal resolution;
- update frequency;
- known limitations;
- whether the data are observed, modeled, crowdsourced, or manually supplied.

Every generated report must include:

- event metadata;
- input data summary;
- exposure estimates;
- priority ranking, if available;
- uncertainty note;
- validation checklist;
- metadata path or provenance record.

### Code Quality

- Prefer simple, readable code over clever code.
- Keep modules small and testable.
- Add type hints for public functions.
- Add docstrings for public functions, classes, and modules.
- Avoid hidden global state.
- Avoid hard-coded file paths.
- Use explicit configuration objects or config files where appropriate.
- Any placeholder function must be clearly marked as `TODO`, `NotImplementedError`, or equivalent.
- Do not introduce heavy dependencies without justification.

---

## Initial Architecture

The package should be organized around these concepts:

- `Event`
- `AOI`
- `HazardLayer`
- `ExposureLayer`
- `InfrastructureLayer`
- `ExposureSummary`
- `PriorityTable`
- `Report`

The architecture should support replaceable adapters rather than hard-coded data sources.

Expected conceptual flow:

```text
Event / AOI
    ↓
Hazard layer
    ↓
Exposure layers + infrastructure layers
    ↓
Exposure summary
    ↓
Priority table
    ↓
Report + map + metadata
```

---

## Recommended Repository Structure

The repository should follow this general structure unless there is a good reason to change it:

```text
disaster-impact-nowcaster/
├── README.md
├── AGENTS.md
├── project_brief.md
├── method_note.md
├── data_sources.md
├── ethics_and_risks.md
├── roadmap.md
├── pyproject.toml
├── .gitignore
├── .github/
│   └── workflows/
│       └── tests.yml
├── src/
│   └── disaster_nowcaster/
│       ├── __init__.py
│       ├── cli.py
│       ├── schemas.py
│       ├── aoi.py
│       ├── events.py
│       ├── hazards.py
│       ├── exposure.py
│       ├── infrastructure.py
│       ├── scoring.py
│       ├── report.py
│       ├── map.py
│       └── metadata.py
├── tests/
├── examples/
├── notebooks/
├── docs/
├── data/
│   └── README.md
└── outputs/
```

The structure may evolve, but early versions should remain simple and easy to inspect.

---

## Initial MVP Scope

The first working version should implement a **static flood exposure and priority report**.

The MVP should accept local files:

- AOI polygon;
- flood or hazard extent polygon/raster;
- administrative boundaries;
- population raster or grid;
- roads layer;
- facilities layer.

The MVP should generate:

- `impact_summary.csv`;
- `priority_areas.csv`;
- `affected_roads.geojson`;
- `affected_facilities.geojson`;
- `map.html`;
- `report.md`;
- `metadata.json`;
- `uncertainty_note.md`.

Do **not** connect real external APIs in the first skeleton unless specifically instructed.

The initial implementation should prioritize:

1. clean package structure;
2. local-file inputs;
3. synthetic test fixtures;
4. reproducible outputs;
5. clear reports;
6. uncertainty documentation.

---

## Command-Line Interface

The initial CLI should eventually support a command similar to:

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

The exact CLI may evolve, but it should remain explicit, reproducible, and scriptable.

---

## Testing

Use `pytest`.

Testing rules:

- Every new module should have at least one minimal test.
- Use small synthetic geometries and rasters for tests.
- Do not rely on external APIs in unit tests.
- Do not rely on network access in unit tests.
- Tests should be deterministic.
- Tests should run in GitHub Actions.

Suggested test categories:

- geometry loading;
- coordinate reference system checks;
- hazard-exposure intersection;
- road-length calculation;
- facility counting;
- population raster summarization;
- priority-score calculation;
- report generation;
- metadata generation.

---

## Outputs

Outputs should be written to an event-specific folder under `outputs/`.

Example:

```text
outputs/demo_event/
├── report.md
├── impact_summary.csv
├── priority_areas.csv
├── affected_roads.geojson
├── affected_facilities.geojson
├── map.html
├── metadata.json
└── uncertainty_note.md
```

Output rules:

- Do not overwrite existing event outputs unless explicitly requested or controlled by a documented `--overwrite` flag.
- Every output folder should include metadata.
- Every report should include an uncertainty note.
- Machine-readable outputs should use stable column names where possible.

---

## Priority Scoring Rules

Priority scoring must be transparent and configurable.

A simple initial structure may be:

```text
priority_score_i =
    w1 * normalized_exposed_population_i
  + w2 * normalized_affected_facilities_i
  + w3 * normalized_road_disruption_i
  + w4 * normalized_vulnerability_proxy_i
```

Rules:

- Do not hard-code normative weights without documenting them.
- Allow weights to be configured.
- Report all component indicators.
- Report the final score and rank.
- State clearly that priority rankings are for decision support, not official allocation.
- Add sensitivity analysis in later versions when feasible.

---

## Uncertainty Requirements

Every report must distinguish:

- exposure from confirmed damage;
- modeled data from observed data;
- preliminary outputs from validated assessments;
- population estimates from actual persons confirmed affected;
- potential infrastructure exposure from verified service disruption.

Reports should include a validation checklist, such as:

- compare with official situation reports;
- compare with Copernicus EMS or UNOSAT products if available;
- check whether hazard data timing matches the event;
- check whether OpenStreetMap roads and facilities are complete;
- check whether population data are outdated;
- check whether urban, vegetation, or terrain conditions affect flood detection;
- check whether local administrative boundaries match operational units.

---

## External Systems and Adapters

This project may eventually connect to or ingest outputs from:

- GDACS;
- Copernicus GFM;
- Copernicus EMS;
- NASA LANCE;
- NASA FIRMS;
- UNOSAT;
- Google FloodHub or flood-forecasting outputs;
- USGS ShakeMap;
- OpenQuake;
- CLIMADA;
- InaSAFE;
- OpenStreetMap / HOT Export Tool;
- WorldPop;
- KoBoToolbox;
- RapidPro;
- Ushahidi;
- Sahana.

Adapter rule:

> Implement adapters as optional, replaceable modules. Do not make the core package depend on one external platform unless necessary.

Early versions should support local files first. API connections should be added only after the local workflow is stable.

---

## Dependency Management

- Use `pyproject.toml` for package metadata and dependencies.
- Keep dependencies minimal in the early version.
- Separate core dependencies from optional dependencies where appropriate.
- Suggested early dependencies may include:
  - `geopandas`;
  - `shapely`;
  - `pandas`;
  - `rasterio`;
  - `pyproj`;
  - `typer` or `click`;
  - `folium` or `leafmap`;
  - `pytest` for testing.
- Do not add large geospatial frameworks without a clear reason.

---

## Git and Pull Request Workflow

When implementing a task:

1. Read `project_brief.md` and `AGENTS.md` first.
2. Identify the smallest coherent change.
3. Modify or add tests.
4. Run tests if possible.
5. Update documentation when behavior changes.
6. Avoid unrelated refactoring.
7. Avoid changing project scope without explicit instruction.
8. Open or prepare a pull request with a concise summary.

A PR summary should include:

- what changed;
- why it changed;
- how it was tested;
- any limitations;
- any follow-up tasks.

---

## Do Not Change Without Explicit Approval

Do not change the following without explicit approval from the project owner:

- project identity or positioning;
- core claim that this project is an integration and prioritization layer;
- repository license;
- public-facing scientific claims;
- ethical and privacy rules;
- output semantics distinguishing exposure from confirmed damage;
- priority-score interpretation;
- major dependencies or framework choices;
- repository structure at a large scale.

---

## First Implementation Task

The first implementation task should be:

> Create a clean Python package skeleton that can load local AOI, hazard, administrative boundary, road, facility, and population inputs; compute simple exposure summaries; generate a Markdown report; generate machine-readable outputs; and run minimal tests using synthetic fixtures.

Do not implement complex remote sensing, real-time API ingestion, or live field-report systems in the first task.

---

## Project Standard

The project should be:

- lightweight;
- open-source;
- reproducible;
- modular;
- well-documented;
- cautious about uncertainty;
- cautious about privacy;
- useful for public decision support;
- honest about limitations.

The guiding principle is:

> Build a small, reliable, inspectable tool that converts existing disaster data into transparent action-support outputs. Do not build an impressive but unverifiable black box.

