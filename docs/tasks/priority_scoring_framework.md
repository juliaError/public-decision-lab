# Priority Scoring Framework Task

## Objective

Design and implement the first rigorous priority-scoring framework for Disaster Impact Nowcaster.

The framework must be:

- literature-informed;
- configurable through explicit YAML files;
- transparent and auditable;
- action-specific rather than a single universal score;
- testable with tiny synthetic data;
- cautious about uncertainty, ethics, and the distinction between exposure and confirmed damage.

## Scope

This stage adds a scoring design document, a baseline flood scoring configuration, a pandas-based scoring module, and unit tests. It does not validate weights, automate official triggers, ingest live field reports, or connect external APIs.

## Required Inputs Reviewed

- `project_brief.md`
- `AGENTS.md`

## Planned Workflow

1. Verify or cautiously document reference frameworks.
2. Add `priority_model_design.md`.
3. Add `configs/priority_models/baseline_flood.yml`.
4. Extend `src/disaster_nowcaster/scoring.py` while preserving the current demo `build_priority_rows` behavior.
5. Add `tests/test_scoring.py`.
6. Update `README.md`, `method_note.md`, and `project_brief.md`.
7. Run tests and inspect generated/documented claims.

## Assumptions

- Default weights are illustrative baseline settings only and must remain editable in YAML.
- Missing required indicators should not be silently imputed.
- Equal-value normalization should use a documented neutral value so tests are deterministic.
- Scores are decision-support indices, not official allocation rules.

## Implementation Log

### v1 Configurable Action-Specific Scoring

- Added `priority_model_design.md` with action-specific priority model design and verified reference anchors.
- Added `configs/priority_models/baseline_flood.yml` with illustrative flood-response score families and explicit weights.
- Extended `src/disaster_nowcaster/scoring.py` with pandas/YAML scoring utilities while preserving the existing demo `build_priority_rows` function.
- Added `tests/test_scoring.py` for normalization, weighted scores, missing required indicators, missing optional indicators, config-driven computation, and data-quality flags.
- Updated `README.md`, `method_note.md`, and `project_brief.md`.
- Added `pandas` and `PyYAML` as lightweight scoring dependencies.

## Verification

- `.venv/bin/python -m pip install -e ".[dev]"`
- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests`
- `.venv/bin/python -m pytest` passed: 13 tests.
- `.venv/bin/disaster-nowcaster run --aoi examples/sample_aoi.geojson --hazard examples/sample_flood_extent.geojson --roads examples/sample_roads.geojson --facilities examples/sample_facilities.geojson --admin examples/sample_admin_units.geojson --population examples/sample_population.tif --output outputs/demo_event --overwrite`
- Checked `outputs/demo_event/priority_areas.csv` and `outputs/demo_event/report.md` to confirm the existing demo path remains cautious and functional.
