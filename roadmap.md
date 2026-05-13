# Roadmap

## v0.1 Static Local Exposure Skeleton

- Load local AOI and hazard polygon GeoJSON files.
- Load local administrative boundary GeoJSON files.
- Load local road and facility GeoJSON files.
- Load optional local population GeoTIFF files.
- Compute simple intersection-based exposure counts.
- Generate Markdown, CSV, GeoJSON, metadata, and static HTML map outputs.
- Run deterministic tests with tiny synthetic fixtures.

## v0.2 Local Data Workflow

- Add stronger CRS and geometry validation.
- Add richer maps and administrative summaries.
- Add optional local population grids beyond GeoTIFF.

## v0.3 Priority Support

- Add transparent, configurable priority-score components.
- Report every score input and weight.
- Add sensitivity checks for alternative weights.

## v0.4 Adapters

- Add optional adapters for external open data sources only after the local workflow is stable.
- Keep adapters replaceable and documented.

## v1.0 Public Release

- Stabilize CLI and Python API.
- Provide full documentation and case studies.
- Include metadata, uncertainty, validation, and reproducibility checks for every report.
