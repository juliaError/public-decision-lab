# Cloud Automation And Remaining Adapters Task

## Objective

Move v0.1 from a local static demo toward a cloud-runnable demo while keeping the first implementation conservative, local-file based, and transparent. This task adds remaining local adapters, a hazard-preparation CLI entry point, a GitHub Actions demo workflow, and a cloud automation design document.

## Scope

This task does not connect to live NASA LANCE, Copernicus GFM, GDACS, or satellite APIs. It does not automatically download real disaster data, publish official reports, or claim validated damage. Outputs remain exposure screening and decision-support artifacts that require local validation.

## Planned Workflow

1. Add a shared local raster-to-hazard GeoJSON helper.
2. Refactor the local NASA LANCE-style adapter to use the shared helper.
3. Add `LocalCopernicusGFMFloodAdapter` for local Copernicus GFM-style rasters.
4. Add `LocalGdacsEventAdapter` for local GDACS-style event manifests.
5. Add `disaster-nowcaster prepare-hazard` CLI commands for local NASA LANCE-style and Copernicus GFM-style rasters.
6. Add GitHub Actions cloud demo workflow that runs the sample v0.1 demo and uploads outputs as an artifact.
7. Add documentation for the future cloud automation architecture.
8. Add tests and run compile/test/demo verification.

## Assumptions

- GitHub Actions is the first cloud target.
- Cloud workflow should be manually triggered first through `workflow_dispatch`; scheduled live polling remains future work.
- Local adapters prepare standardized local artifacts and metadata; the core pipeline continues to consume local files.
- All language must distinguish estimated exposure from confirmed damage and decision-support scores from official allocation.

## Implementation Log

### v1 Planned Conservative Cloud-Ready Demo

- Added shared raster-to-hazard helper in `adapters/raster_hazard.py`.
- Refactored `LocalNasaLanceFloodAdapter` to use the shared helper.
- Added `LocalCopernicusGFMFloodAdapter` for local Copernicus GFM-style flood rasters.
- Added `LocalGdacsEventAdapter` for local GDACS-style event manifests.
- Added `disaster-nowcaster prepare-hazard nasa-lance-local`.
- Added `disaster-nowcaster prepare-hazard copernicus-gfm-local`.
- Added manually triggered GitHub Actions cloud demo workflow at `.github/workflows/cloud-demo.yml`.
- Added `docs/cloud_automation.md` describing future GDACS-triggered cloud automation.
- Updated adapter contract, data-source notes, and README.
- Status: implemented locally.

### v2 PR-Compatible Branch

- Configured `origin` as `https://github.com/juliaError/public-decision-lab`.
- Pushed the original local branch `codex/initialize-repository`, but GitHub could not create a PR because it had no shared history with `main`.
- Created `codex/initialize-repository-pr` from `origin/main` and copied the implemented project tree onto it.
- Preserved the existing remote `LICENSE`; this task does not change the repository license.

## Verification

- `PYTHONPYCACHEPREFIX=/private/tmp/disaster_nowcaster_pycache .venv/bin/python -m compileall src tests` passed.
- `.venv/bin/python -m pytest` passed: 46 tests, with one local urllib3 LibreSSL warning.
- `.venv/bin/disaster-nowcaster run --aoi examples/sample_aoi.geojson --hazard examples/sample_flood_extent.geojson --roads examples/sample_roads.geojson --facilities examples/sample_facilities.geojson --admin examples/sample_admin_units.geojson --population examples/sample_population.tif --output outputs/demo_event --overwrite` passed and wrote 7 expected files.
- Workflow YAML parsed with PyYAML.

## Unresolved TODOs

- `gh auth status` still reports an invalid token for the active account, although `git push` worked through the available git credentials.
- The GitHub Actions cloud demo can only be fully verified after the workflow runs on GitHub.
- Live GDACS polling, NASA LANCE download, and Copernicus GFM download remain future work.
