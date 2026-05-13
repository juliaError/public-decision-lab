# Case Study Template

## Case Metadata

- Case ID:
- Event name:
- Country/region:
- Hazard type:
- Event dates:
- Case status:
- Analyst:
- Last updated:

## Evaluation Purpose

Explain why this case is useful for evaluating Disaster Impact Nowcaster. State which capabilities are being tested, such as population exposure, infrastructure exposure, road access, health facility exposure, priority ranking, report clarity, or cloud automation.

## Event Summary

Summarize the event using traceable sources. Do not present model outputs as confirmed impacts.

Required distinction:

- what was known during the event;
- what was learned after the event;
- what remains uncertain.

## Source Inventory

| Source title | Publisher | URL/path | Date accessed | Event-time coverage | Use in case |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | input / validation / narrative |

## Timeline

| Time | Event or action | Source | Notes |
| --- | --- | --- | --- |
|  |  |  |  |

## Input Data

| Input | Source | Local path or external location | Available by | Limitations |
| --- | --- | --- | --- | --- |
| AOI |  |  |  |  |
| Hazard |  |  |  |  |
| Admin units |  |  |  |  |
| Population |  |  |  |  |
| Roads |  |  |  |  |
| Facilities |  |  |  |  |

## Run Log

Record each run separately. For retrospective work, note the data cut-off.

```bash
disaster-nowcaster run \
  --aoi <path> \
  --hazard <path> \
  --roads <path> \
  --facilities <path> \
  --admin <path> \
  --population <path> \
  --output outputs/<case_id>/<run_id>
```

## System Outputs

| Output | Path | Notes |
| --- | --- | --- |
| report.md |  |  |
| impact_summary.csv |  |  |
| priority_areas.csv |  |  |
| affected_roads.geojson |  |  |
| affected_facilities.geojson |  |  |
| map.html |  |  |
| metadata.json |  |  |

## Evaluation

### Exposure Summary

- What did the system identify?
- Did later evidence suggest those areas were relevant?
- Were there important affected areas that the system missed?

### Priority Ranking

- Which areas appeared in the top-k priority list?
- Did those areas correspond to later reported hotspots or response focus areas?
- Did the score reflect need, access constraints, or only data availability?

### Infrastructure And Access

- Which roads or facilities were potentially exposed?
- Did public reporting mention related access, medical, shelter, or service issues?
- Were OSM or local infrastructure data incomplete?

### Timeliness

- Could the run have happened before relevant response actions?
- Which data source was the bottleneck?
- Would cloud automation have changed the timing?

### Usefulness Judgment

Choose one and explain:

- `useful_as_is_for_review`;
- `useful_with_data_upgrade`;
- `useful_with_scoring_upgrade`;
- `not_useful_yet`;
- `insufficient_evidence`.

## Upgrade Decisions

| Issue found | Proposed upgrade | Priority | Owner/status |
| --- | --- | --- | --- |
|  |  |  |  |

## Ethical And Operational Notes

- Could any output reveal sensitive locations?
- Could any public map be misread as confirmed damage?
- Would responders need access control?
- What validation should happen before sharing?

## Technical Report Notes

List the key figures, tables, quotes, or lessons that may enter the final technical report.
