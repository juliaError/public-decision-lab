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
- Equal-value normalization should use a documented zero discriminatory contribution so tests are deterministic and users do not read it as zero underlying risk.
- Scores are decision-support indices, not official allocation rules.
- Optional missing indicators should be flagged and available weights should be renormalized by default.
- Feasibility is not need; cash feasibility should be reported separately from cash need.

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

### v2 Semantic Safety Revision

- Strengthen YAML with an indicator catalog, score entity metadata, explicit indicator directions, model completeness flags, and optional-missing renormalization.
- Add config validation for required keys, indicator catalog coverage, entity levels, directions, formulas, and weight sums.
- Separate cash need, cash feasibility, and cash review score so delivery feasibility does not silently suppress humanitarian need.
- Clarify road repair benefit-over-cost outputs and safe cost handling.
- Expand tests for validation failures, direction handling, optional missing renormalization, row-level required missing values, road cost edge cases, score entity metadata, and data-quality versus model-completeness flags.

## v2 Verification

- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests`
- `.venv/bin/python -m pytest` passed: 24 tests.
- `.venv/bin/disaster-nowcaster run --aoi examples/sample_aoi.geojson --hazard examples/sample_flood_extent.geojson --roads examples/sample_roads.geojson --facilities examples/sample_facilities.geojson --admin examples/sample_admin_units.geojson --population examples/sample_population.tif --output outputs/demo_event --overwrite`
- Checked that this revision does not add external APIs, satellite-data integration, validated-score claims, or official allocation claims.

### v3 Pre-Merge Scoring Review Fixes

- Added `derived_score` as a valid indicator role and updated `need_severity` catalog metadata.
- Added entity-level compatibility validation across raw indicators, derived score references, and formula references.
- Added validation that weighted score required and optional indicators exactly match the configured weight keys.
- Fixed `cash_priority` propagation so missing or incomplete feasibility information is reflected in its missing optional indicators and completeness flags.
- Clarified that component columns use original configured weights while final scores may use row-level available-weight renormalization.
- Documented that v0.1 `data_quality_flag` is a completeness-based proxy, not a full data-quality assessment.
- Strengthened road repair tests for missing optional repair difficulty, missing required segment length, equal cost terms, invalid epsilon, aid-route renormalization, and row-level missing required cost data.

## v3 Verification

- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests`
- `.venv/bin/python -m pytest` passed: 33 tests.
- `.venv/bin/disaster-nowcaster run --aoi examples/sample_aoi.geojson --hazard examples/sample_flood_extent.geojson --roads examples/sample_roads.geojson --facilities examples/sample_facilities.geojson --admin examples/sample_admin_units.geojson --population examples/sample_population.tif --output outputs/demo_event --overwrite`
