# Case Study Evaluation Framework Task

## Objective

Define a retrospective case-study evaluation workflow before building additional product surfaces such as a WeChat Mini Program. The goal is to test whether Disaster Impact Nowcaster would have provided useful situational-awareness, exposure-screening, and priority-review outputs in past disasters, and to identify what must be improved before operational use.

## Scope

This task does not run real historical case pipelines yet. It creates the evaluation protocol, case-study template, candidate case registry, and final technical report outline. It should not fabricate data, impact claims, or conclusions about system usefulness. Historical findings must be based on traceable sources and reproducible runs.

## Planned Workflow

1. Create a case-study evaluation plan.
2. Create a case-study template and folder README.
3. Create an initial candidate case registry with source leads.
4. Create a final technical report outline.
5. Document safeguards for retrospective evaluation, including no hindsight leakage and no unsupported causal claims.

## Implementation Log

### v1 Evaluation Framework

- Created `docs/case_study_evaluation_plan.md`.
- Created `docs/case_studies/README.md`.
- Created `docs/case_studies/case_template.md`.
- Created `configs/case_studies/candidate_cases.yml`.
- Created `docs/technical_report_outline.md`.
- Updated `roadmap.md` with retrospective case evaluation and technical report stages.
- Merged PR #3 into `main` as the evaluation-framework baseline.

### v2 Case Tooling And Zhengzhou First Case

- Added case-study manifest validation utilities in `src/disaster_nowcaster/cases.py`.
- Added `disaster-nowcaster case validate`.
- Added `disaster-nowcaster case scaffold`.
- Added tests for manifest validation failures and scaffold generation.
- Added first case manifest: `configs/case_studies/cn_henan_zhengzhou_flood_2021.yml`.
- Added Zhengzhou case source inventory, case note, run log, and evaluation placeholder under `docs/case_studies/cn_henan_zhengzhou_flood_2021/`.
- Marked the Zhengzhou case as `data_gap` because no trustworthy flood polygon has been prepared yet.
- Status: implemented locally.

### v3 Continue Iteration Beyond Zhengzhou

- User clarified that a Zhengzhou hazard-data gap should not stop the iteration.
- Selected the Pakistan / Sindh / Khairpur Nathan Shah 2022 flood as the next historical replay candidate because UNOSAT/HDX exposes a public machine-readable flood-water vector package.
- Added `configs/case_studies/pk_sindh_khairpur_flood_2022.yml`.
- Added Pakistan case source inventory, case note, run log, and evaluation note under `docs/case_studies/pk_sindh_khairpur_flood_2022/`.
- Verified through the HDX CKAN API that the UNOSAT Khairpur dataset has:
  - zipped shapefile resource: about 286 MB;
  - small population exposure workbook: about 12.9 KB;
  - CC BY-SA license metadata;
  - explicit UNOSAT caveat that the analysis is preliminary and not field validated.
- Attempted the large shapefile download to `/private/tmp`, stopped it because the connection was too slow for the interactive session, and did not use the partial file.
- Downloaded the small UNOSAT exposure workbook to `/private/tmp` and inspected its district-level columns for diagnostic context only.
- Added case output checking utilities:
  - `check_case_output_files`;
  - `validate_case_output_files`;
  - `disaster-nowcaster case check-outputs --output <dir>`.
- Updated `configs/case_studies/candidate_cases.yml` so the Pakistan case now points to concrete source leads and the focused Khairpur case manifest.
- Status: Pakistan/Khairpur is not a completed run yet, but the iteration has moved from an unresolved Zhengzhou data gap to a concrete external-data preparation target.

## Verification

- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests` passed.
- `.venv/bin/python -m pytest` passed: 56 tests, with one local urllib3 LibreSSL warning.
- `.venv/bin/python -c "import yaml; from pathlib import Path; paths=sorted(Path('configs/case_studies').glob('*.yml')); [yaml.safe_load(p.read_text()) for p in paths]; print('parsed case yaml:', len(paths))"` parsed 2 YAML files.
- `.venv/bin/disaster-nowcaster case validate --manifest configs/case_studies/cn_henan_zhengzhou_flood_2021.yml` passed.
- `git diff --check` passed.
- Method-safety text search found only negative/cautionary uses of terms such as `confirmed damage`, `confirmed victims`, and `official allocation`.
- `.venv/bin/disaster-nowcaster case validate --manifest configs/case_studies/pk_sindh_khairpur_flood_2022.yml` passed.
- `.venv/bin/disaster-nowcaster case check-outputs --output outputs/demo_event` found all 7 core v0.1 output files in the local sample demo output.
- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests` passed after v3 changes.
- `.venv/bin/python -m pytest` passed after v3 changes: 61 tests, with one local urllib3 LibreSSL warning.
- `git diff --check` passed after v3 changes.
