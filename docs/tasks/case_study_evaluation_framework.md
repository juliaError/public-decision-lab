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

## Verification

- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests` passed.
- `.venv/bin/python -m pytest` passed: 56 tests, with one local urllib3 LibreSSL warning.
- `.venv/bin/python -c "import yaml; from pathlib import Path; paths=sorted(Path('configs/case_studies').glob('*.yml')); [yaml.safe_load(p.read_text()) for p in paths]; print('parsed case yaml:', len(paths))"` parsed 2 YAML files.
- `.venv/bin/disaster-nowcaster case validate --manifest configs/case_studies/cn_henan_zhengzhou_flood_2021.yml` passed.
- `git diff --check` passed.
- Method-safety text search found only negative/cautionary uses of terms such as `confirmed damage`, `confirmed victims`, and `official allocation`.
