# Disaster Impact Nowcaster

Disaster Impact Nowcaster is a lightweight, open-source, reproducible layer for turning existing disaster hazard data and local exposure data into transparent exposure summaries, maps, reports, and cautious decision-support outputs.

The project answers a narrow first question: given an area of interest, a hazard layer, administrative units, local infrastructure files, and an optional local population raster, what population and infrastructure are potentially exposed, and which administrative units should be reviewed first?

It does not forecast hazards, replace official agencies, identify people, confirm damage, verify service disruption, or make official allocation decisions.

**中文**

Disaster Impact Nowcaster 是一个轻量、开源、可复现的灾害影响 nowcasting 与行动优先级辅助层。它把已有灾害 hazard 数据、本地 exposure 数据、基础设施数据转成透明的暴露估计、地图、报告和谨慎的决策支持输出。

这个项目第一阶段只回答一个窄问题：给定一个关注区域、灾害范围图层、行政区、本地基础设施文件，以及可选的人口栅格，哪些人口和基础设施可能暴露在灾害范围内？哪些行政区应优先被人工复核？

它不预测灾害，不替代官方机构，不识别个人，不确认损失，不验证服务中断，也不做官方资源分配决定。

## What v0.1 Does

The current v0.1 workflow can:

- load an AOI polygon GeoJSON;
- load a hazard polygon GeoJSON;
- load administrative boundary GeoJSON;
- load infrastructure GeoJSON or GeoPackage files exported from sources such as OSM/HOT;
- load an optional local population raster GeoTIFF;
- count features that intersect both the AOI and hazard extent;
- estimate exposed population by clipping raster cells to the hazard extent;
- write `report.md`, `impact_summary.csv`, `priority_areas.csv`, affected infrastructure GeoJSON files, `map.html`, and `metadata.json`;
- run locally from the CLI or manually in GitHub Actions.

The sample files in `examples/` are tiny synthetic fixtures for testing the workflow. They are not real disaster observations and do not contain real WorldPop data.

**中文**

当前 v0.1 工作流可以：

- 读取 AOI 多边形 GeoJSON；
- 读取 hazard 多边形 GeoJSON；
- 读取行政边界 GeoJSON；
- 读取从 OSM/HOT 等来源导出的基础设施 GeoJSON 或 GeoPackage；
- 读取可选的本地人口栅格 GeoTIFF；
- 统计同时与 AOI 和 hazard 范围相交的要素；
- 通过 hazard 范围裁剪人口栅格，估计暴露人口；
- 输出 `report.md`、`impact_summary.csv`、`priority_areas.csv`、受影响基础设施 GeoJSON、`map.html` 和 `metadata.json`；
- 通过 CLI 在本地运行，也可以在 GitHub Actions 中手动运行。

`examples/` 里的样例文件都是很小的合成测试数据。它们不是真实灾害观测，也不包含真实 WorldPop 数据。

## Install

```bash
python -m pip install -e ".[dev]"
```

The package uses `rasterio` for local GeoTIFF population rasters. The `dev` extra installs `pytest`.

**中文**

安装命令如下：

```bash
python -m pip install -e ".[dev]"
```

本包使用 `rasterio` 读取本地 GeoTIFF 人口栅格。`dev` 额外依赖会安装 `pytest`，用于运行测试。

## Run The Demo

```bash
disaster-nowcaster run \
  --aoi examples/sample_aoi.geojson \
  --hazard examples/sample_flood_extent.geojson \
  --roads examples/sample_roads.geojson \
  --facilities examples/sample_facilities.geojson \
  --admin examples/sample_admin_units.geojson \
  --population examples/sample_population.tif \
  --output outputs/demo_event
```

If `outputs/demo_event` already exists from an earlier run, add `--overwrite` to regenerate the demo outputs.

Equivalent module invocation before installation:

```bash
python -m disaster_nowcaster.cli run \
  --aoi examples/sample_aoi.geojson \
  --hazard examples/sample_flood_extent.geojson \
  --roads examples/sample_roads.geojson \
  --facilities examples/sample_facilities.geojson \
  --admin examples/sample_admin_units.geojson \
  --population examples/sample_population.tif \
  --output outputs/demo_event
```

**中文**

运行静态 demo：

```bash
disaster-nowcaster run \
  --aoi examples/sample_aoi.geojson \
  --hazard examples/sample_flood_extent.geojson \
  --roads examples/sample_roads.geojson \
  --facilities examples/sample_facilities.geojson \
  --admin examples/sample_admin_units.geojson \
  --population examples/sample_population.tif \
  --output outputs/demo_event
```

如果 `outputs/demo_event` 已经存在，可以添加 `--overwrite` 重新生成 demo 输出。

在尚未安装命令行入口前，也可以用模块方式运行：

```bash
python -m disaster_nowcaster.cli run \
  --aoi examples/sample_aoi.geojson \
  --hazard examples/sample_flood_extent.geojson \
  --roads examples/sample_roads.geojson \
  --facilities examples/sample_facilities.geojson \
  --admin examples/sample_admin_units.geojson \
  --population examples/sample_population.tif \
  --output outputs/demo_event
```

## Prepare Local Raster Hazards

Local flood rasters can be converted into the hazard GeoJSON expected by the demo pipeline:

```bash
disaster-nowcaster prepare-hazard nasa-lance-local \
  --raster path/to/local_flood.tif \
  --output outputs/prepared_hazard.geojson \
  --flood-value 1

disaster-nowcaster prepare-hazard copernicus-gfm-local \
  --raster path/to/local_gfm_flood.tif \
  --output outputs/prepared_hazard.geojson \
  --flood-value 1
```

These commands only prepare local input files. They do not download satellite data, validate flood-product semantics, or confirm damage.

**中文**

本地 flood raster 可以先转成 demo pipeline 所需的 hazard GeoJSON：

```bash
disaster-nowcaster prepare-hazard nasa-lance-local \
  --raster path/to/local_flood.tif \
  --output outputs/prepared_hazard.geojson \
  --flood-value 1

disaster-nowcaster prepare-hazard copernicus-gfm-local \
  --raster path/to/local_gfm_flood.tif \
  --output outputs/prepared_hazard.geojson \
  --flood-value 1
```

这些命令只准备本地输入文件。它们不会下载卫星数据，不会验证 flood 产品语义，也不会确认灾害损失。

## Outputs

The demo writes an event output folder such as `outputs/demo_event/` containing:

- `impact_summary.csv`: metric/value exposure summary, including estimated exposed population when `--population` is provided;
- `priority_areas.csv`: admin-level demo ranking with exposed infrastructure counts and estimated exposed population;
- `affected_roads.geojson`: road features that intersect both AOI and hazard polygon, with input-CRS hazard-intersection length;
- `affected_facilities.geojson`: supported hospital, clinic, school, and shelter features that intersect both AOI and hazard polygon;
- `map.html`: interactive Folium/Leaflet map with AOI, hazard, affected facilities, and admin priority choropleth layers;
- `metadata.json`: input paths, method summary, and claims limit;
- `report.md`: a short human-readable Markdown report.

**中文**

demo 会写入一个事件输出文件夹，例如 `outputs/demo_event/`，其中包括：

- `impact_summary.csv`：指标和值形式的暴露摘要；如果提供 `--population`，会包含估计暴露人口；
- `priority_areas.csv`：行政区级 demo 排序，包含暴露基础设施计数和估计暴露人口；
- `affected_roads.geojson`：同时与 AOI 和 hazard 多边形相交的道路要素，并包含输入坐标系单位下的 hazard 相交长度；
- `affected_facilities.geojson`：同时与 AOI 和 hazard 多边形相交的医院、诊所、学校、避难所等设施要素；
- `map.html`：基于 Folium/Leaflet 的交互地图，包含 AOI、hazard、受影响设施和行政区优先级图层；
- `metadata.json`：输入路径、方法摘要和声明边界；
- `report.md`：面向人工阅读的简短 Markdown 报告。

## Interpretation Language

Reports use cautious terminology:

- estimated exposure, not confirmed damage;
- estimated exposed population, not confirmed affected people;
- potentially affected roads, not destroyed roads;
- facilities located within the hazard extent, not verified service disruptions;
- demo priority score, not official allocation priority.

**中文**

报告使用谨慎表述：

- estimated exposure，而不是 confirmed damage；
- estimated exposed population，而不是 confirmed affected people；
- potentially affected roads，而不是 destroyed roads；
- facilities located within the hazard extent，而不是 verified service disruptions；
- demo priority score，而不是 official allocation priority。

## Limitations

- The workflow supports local GeoJSON inputs, local GeoPackage infrastructure inputs, and local population GeoTIFF inputs.
- It supports local OSM/HOT-style GeoJSON or GeoPackage infrastructure extracts.
- It does not download WorldPop or OSM data and does not call external APIs.
- Population rasters and vector files must already use the same coordinate reference system.
- Road length is measured in input CRS units.
- The built-in geometry checks are minimal and intended for tiny synthetic fixtures, not complex real-world topology.
- It reports exposure screening only; every result requires validation against official reports and local knowledge.
- Automatic WorldPop download, reprojection, advanced geospatial operations, and validated local priority calibration are future work.

**中文**

- 当前工作流支持本地 GeoJSON、本地 GeoPackage 基础设施输入，以及本地人口 GeoTIFF 输入。
- 它支持本地 OSM/HOT 风格的 GeoJSON 或 GeoPackage 基础设施抽取文件。
- 它不会下载 WorldPop 或 OSM 数据，也不会调用外部 API。
- 人口栅格和矢量文件必须已经使用同一坐标参考系统。
- 道路长度以输入坐标系单位计算。
- 内置几何检查非常基础，主要服务于小型合成测试数据，不适合复杂真实世界拓扑。
- 它只报告 exposure screening；每个结果都需要与官方报告和本地知识交叉验证。
- 自动 WorldPop 下载、重投影、高级地理处理和经本地校准的优先级模型都是未来工作。

## Priority Scoring

Priority scoring is configurable and action-specific. The repository includes a baseline flood-response YAML model at `configs/priority_models/baseline_flood.yml` and scoring utilities in `src/disaster_nowcaster/scoring.py`.

Scores are decision-support indices, not official allocation rules. Default weights are illustrative baseline settings only; users should adapt weights to local objectives, constraints, data quality, and stakeholder review. Exposure does not equal confirmed damage, and all priority outputs must be locally validated before use.

The first scoring framework supports separate score families for need severity, lifeline disruption, rescue review, cash-transfer support, health support, and road repair review. Score weights are configurable, indicator directions are explicit, and missing optional indicators are flagged while available weights are renormalized. Feasibility is reported separately from need so easier delivery does not silently redefine humanitarian severity. The design rationale is documented in `priority_model_design.md`.

**中文**

优先级评分是可配置、面向具体行动目标的。仓库中提供了一个基线洪水响应 YAML 模型：`configs/priority_models/baseline_flood.yml`，评分工具在 `src/disaster_nowcaster/scoring.py`。

这些分数是决策支持指数，不是官方资源分配规则。默认权重只是说明性的 baseline 设置；使用者应根据本地目标、约束、数据质量和利益相关方审查来调整权重。暴露不等于确认损失，所有优先级输出在使用前都必须经过本地验证。

第一版评分框架支持 need severity、lifeline disruption、rescue review、cash-transfer support、health support 和 road repair review 等不同 score family。权重可配置，指标方向明确，缺失的 optional indicator 会被标记，且可用权重会重新归一化。可达性和可执行性会与实际需求分开报告，避免“更容易送达”被误当作“更需要援助”。设计说明见 `priority_model_design.md`。

## Adapter Contract

The repository includes an adapter contract for future data-source integrations. Adapters prepare standardized local artifacts plus source metadata; the core pipeline still consumes local files.

Current adapter support is intentionally local-only:

- `LocalHazardAdapter` wraps an existing local hazard GeoJSON.
- `LocalNasaLanceFloodAdapter` converts an existing local NASA LANCE-style flood GeoTIFF into hazard GeoJSON using a configurable threshold.
- `LocalCopernicusGFMFloodAdapter` converts an existing local Copernicus GFM-style flood GeoTIFF into hazard GeoJSON using a configurable threshold.
- `LocalGdacsEventAdapter` reads a local GDACS-style event manifest JSON into internal event metadata.
- No NASA LANCE, Copernicus GFM, GDACS, WorldPop, OSM, or satellite-data API is called automatically.
- Adapter outputs remain inputs for exposure screening, not confirmed damage or official priority information.

See `docs/adapter_contract.md`.

**中文**

仓库包含一个面向未来数据源集成的 adapter contract。Adapter 负责准备标准化本地 artifacts 和来源 metadata；核心 pipeline 仍然消费本地文件。

当前 adapter 支持故意保持 local-only：

- `LocalHazardAdapter` 包装已有本地 hazard GeoJSON。
- `LocalNasaLanceFloodAdapter` 使用可配置阈值，将已有本地 NASA LANCE-style flood GeoTIFF 转成 hazard GeoJSON。
- `LocalCopernicusGFMFloodAdapter` 使用可配置阈值，将已有本地 Copernicus GFM-style flood GeoTIFF 转成 hazard GeoJSON。
- `LocalGdacsEventAdapter` 把本地 GDACS-style event manifest JSON 读成内部事件 metadata。
- 不会自动调用 NASA LANCE、Copernicus GFM、GDACS、WorldPop、OSM 或卫星数据 API。
- Adapter 输出只是 exposure screening 的输入，不是确认损失，也不是官方优先级信息。

参见 `docs/adapter_contract.md`。

## Cloud Demo

`.github/workflows/cloud-demo.yml` can run the static v0.1 demo in GitHub Actions using `workflow_dispatch` and upload the generated output folder as an artifact. This is a cloud-runnable demo, not a live disaster trigger.

The future automation design is documented in `docs/cloud_automation.md`: GDACS event polling, duplicate checks, local standardized data preparation, nowcaster execution, artifact storage, and a validation gate before publication.

**中文**

`.github/workflows/cloud-demo.yml` 可以通过 GitHub Actions 的 `workflow_dispatch` 手动运行静态 v0.1 demo，并把生成的输出文件夹上传为 artifact。这是一个可在云端运行的 demo，不是实时灾害触发系统。

未来自动化设计写在 `docs/cloud_automation.md`：GDACS 事件轮询、重复事件检查、本地标准化数据准备、nowcaster 运行、artifact 存储，以及发布前的 validation gate。

## Tests

```bash
python -m pytest
```

Tests use tiny synthetic GeoJSON and GeoTIFF fixtures and do not require network access. GitHub Actions runs the same test suite on push and pull request.

**中文**

运行测试：

```bash
python -m pytest
```

测试使用很小的合成 GeoJSON 和 GeoTIFF fixture，不需要网络访问。GitHub Actions 会在 push 和 pull request 时运行同一套测试。
