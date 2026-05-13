# Initialize Repository Task

## Objective

Create the first minimal working skeleton for Disaster Impact Nowcaster.

The skeleton must:

- load local AOI GeoJSON;
- load local hazard polygon GeoJSON;
- load local infrastructure point and line GeoJSON;
- compute simple intersection-based exposure counts;
- generate a Markdown report and machine-readable outputs;
- expose a CLI command;
- include pytest tests with tiny synthetic fixtures;
- avoid real external APIs, fabricated scientific claims, and large committed data.

## Context Read

- v1 context read: `project_brief.md` and `AGENTS.md` were read before implementation.
- Local state: repository directory initially contained only `agents.md`/`AGENTS.md` and `project_brief.md`.
- Git state: no `.git` repository existed at task start; initial `git init` attempt was blocked by filesystem permissions.

## Workflow Log

### v1 Minimal Skeleton

1. Create a small package using only Python standard-library runtime dependencies.
2. Implement lightweight GeoJSON loading and simple geometry intersection logic for synthetic/local polygon, point, and line inputs.
3. Generate cautious exposure language: exposure counts are not confirmed damage.
4. Add tests and tiny synthetic fixtures.
5. Run the smallest available verification.
6. Initialize git and open a PR if repository remote access is available.

### Verification Notes

- First compile attempt showed the local `python3` is Python 3.9 and cannot import `datetime.UTC`; updated the package to support Python 3.9+ with `datetime.timezone.utc`.
- Python bytecode cache writes to `~/Library/Caches` are blocked in this sandbox; verification should set `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache`.
- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache python3 -m compileall src tests` passed.
- `PYTHONPATH=src python3 -m disaster_nowcaster.cli run ... --output outputs/demo_event --overwrite` generated 6 files with 1 potentially affected road and 1 facility located within the hazard extent.
- `.venv/bin/python -m pytest` passed: 2 tests passed.

### v2 Review Against Project-Owner Checklist

The user requested a pre-merge check of:

1. repository structure cleanliness;
2. fake data or unsupported claims;
3. local and GitHub Actions testability;
4. README clarity for an external reader.

Changes made in v2:

- Added root documentation files: `method_note.md`, `data_sources.md`, `ethics_and_risks.md`, and `roadmap.md`.
- Renamed the hazard module from `hazards.py` to `hazard.py` to match the target structure.
- Added `scoring.py` with a `NotImplementedError` placeholder, making clear that priority scoring is not implemented in the skeleton.
- Added `dev` dependency extra and updated GitHub Actions and README to use `pip install -e ".[dev]"`.
- Expanded README to state the problem, non-goals, demo command, outputs, and limitations within the first page.
- Rechecked wording for exposure-only language and synthetic fixture labeling.

Verification after v2:

- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache python3 -m compileall src tests` passed.
- `.venv/bin/python -m pip install -e ".[dev]"` passed after upgrading local virtualenv pip and allowing network access for build dependencies.
- `.venv/bin/disaster-nowcaster run ... --output outputs/demo_event --overwrite` generated the expected 6 demo files.
- `.venv/bin/python -m pytest` passed: 2 tests passed.

## Open Items

- Local git repository was initialized with escalation.
- Local branch: `codex/initialize-repository`.
- Local commit message: `Initialize disaster nowcaster skeleton`.
- PR creation is blocked because no `origin` remote is configured and `gh auth status` reports an invalid GitHub token for account `juliaError`.

## v0.1 Static Demo Task

Objective update:

- Build a static v0.1 demo using only local sample files.
- Add `examples/sample_admin_units.geojson`.
- Support the command:
  `disaster-nowcaster run --aoi examples/sample_aoi.geojson --hazard examples/sample_flood_extent.geojson --roads examples/sample_roads.geojson --facilities examples/sample_facilities.geojson --admin examples/sample_admin_units.geojson --output outputs/demo_event`
- Generate `report.md`, `impact_summary.csv`, `priority_areas.csv`, `affected_facilities.geojson`, `affected_roads.geojson`, `map.html`, and `metadata.json`.
- Keep language cautious: estimated exposure, potentially affected infrastructure, not confirmed damage, requires validation.
- Make README sufficient for a non-coder to run the demo and obtain a disaster impact report.

Implementation plan:

1. Add admin loading and sample admin-unit GeoJSON.
2. Compute admin-level `priority_areas.csv` using a documented demo score.
3. Generate a self-contained `map.html`.
4. Update CLI, report, metadata, tests, and README around the exact v0.1 command and output tree.

Implementation completed:

- Added admin loading through `src/disaster_nowcaster/admin.py`.
- Added `examples/sample_admin_units.geojson` and `tests/fixtures/admin.geojson`.
- Added admin-level priority rows with `demo_priority_score = potentially affected road count + facilities within hazard extent count`.
- Added self-contained SVG/HTML map output in `map.html`.
- Updated README so a non-coder can install, run the static demo, and inspect the output folder.

Verification after v0.1:

- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache python3 -m compileall src tests` passed.
- `.venv/bin/python -m pip install -e ".[dev]"` passed after allowing network access for build dependencies.
- `.venv/bin/disaster-nowcaster run --aoi examples/sample_aoi.geojson --hazard examples/sample_flood_extent.geojson --roads examples/sample_roads.geojson --facilities examples/sample_facilities.geojson --admin examples/sample_admin_units.geojson --output outputs/demo_event` passed without `--overwrite` from a clean output path.
- Generated output folder contains exactly: `report.md`, `impact_summary.csv`, `priority_areas.csv`, `affected_facilities.geojson`, `affected_roads.geojson`, `map.html`, and `metadata.json`.
- `.venv/bin/python -m pytest` passed: 2 tests passed.
- Unsupported-claim scan found no positive claims like actual victims, confirmed losses, or exact affected people.
