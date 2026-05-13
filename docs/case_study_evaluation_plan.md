# Case Study Evaluation Plan

## Purpose

Before expanding Disaster Impact Nowcaster into a public-facing reporting tool, the project should be tested against past disasters. The goal is not to prove that the system is universally useful. The goal is to learn, with evidence, when it helps, when it fails, and what must be upgraded.

The evaluation should answer four practical questions:

1. Would the system have produced a useful early exposure and priority picture?
2. Would it have surfaced areas, infrastructure, or access constraints that were later important in public reporting or response records?
3. Would it have reduced manual screening work for analysts, responders, or local coordinators?
4. What data, models, or workflow changes are needed before the system can be trusted for stronger operational use?

All outputs remain decision support. Exposure is not confirmed damage. Priority ranks are not official allocation rules.

## Case Study Logic

Each case should be a retrospective event replay. The system should be run using data that would plausibly have been available at specific points in the event timeline, such as:

- pre-event baseline data;
- early hazard extent or forecast products;
- updated hazard observations;
- later validation or situation reports.

The evaluation must separate two modes:

- **Real-time simulation mode:** uses only data that were available by a chosen time cut-off.
- **Post-event diagnostic mode:** uses later data to understand errors, missed signals, and upgrade opportunities.

Do not use hindsight data in a real-time simulation and then claim the system would have known that information during the event.

## Candidate Case Selection

Start with a small set of contrasting cases. A useful case should have:

- publicly documented event timeline;
- public government, humanitarian, or reputable news reporting;
- at least one hazard layer, map, or reconstructable event footprint;
- available population and infrastructure baseline data;
- identifiable response actions or operational bottlenecks;
- enough geographic specificity to compare against administrative units or known affected areas;
- manageable sensitivity risks.

Avoid cases where precise public mapping of vulnerable individuals or sensitive sites could create harm.

## Initial Candidate Cases

These are candidates, not findings. Each must be checked before use.

| Candidate case | Why it may be useful | Source leads to verify |
| --- | --- | --- |
| 2021 Henan / Zhengzhou extreme rainfall and flooding | Dense urban exposure, transport disruption, emergency response timeline, and official investigation material. | State Council investigation report on the Zhengzhou 7.20 extreme rainfall disaster; provincial and municipal official materials; reputable news archives. |
| 2023 Beijing-Tianjin-Hebei / Haihe Basin flooding after Typhoon Doksuri | Large rainfall footprint, evacuations, transport and access issues, upstream-downstream coordination questions. | Ministry of Emergency Management, Ministry of Water Resources, local government notices, official situation reports, reputable news archives. |
| 2022 Pakistan floods | Large-scale exposure estimation, admin-level prioritization, population exposure, humanitarian response documentation. | Pakistan government materials, UN OCHA situation reports, satellite-derived flood products, humanitarian response documents. |
| 2023 Libya Derna flooding | High-consequence flash flood/dam-failure context with severe data and validation limits. | Copernicus EMS materials, UN OCHA updates, official or humanitarian reports, reputable news archives. |

The first two cases are especially relevant for future China-facing public use. The Pakistan and Libya cases are useful for testing whether the system handles large-scale and data-limited settings.

## Evidence Collection Protocol

For each case, collect evidence in four groups:

1. **Event timeline**
   - hazard onset;
   - official warnings;
   - first public situation reports;
   - major evacuation or rescue actions;
   - later official assessments.

2. **Response actions**
   - evacuation orders or shelter openings;
   - road closures or transport interruptions;
   - rescue deployments;
   - medical or supply distribution;
   - public reporting of bottlenecks.

3. **Input data**
   - AOI and administrative boundaries;
   - hazard extent or forecast layer;
   - population raster or gridded population;
   - roads and facilities;
   - optional vulnerability or capacity indicators.

4. **Validation and comparison evidence**
   - official situation reports;
   - post-event investigation reports;
   - satellite rapid maps;
   - humanitarian response reports;
   - reputable local reporting.

Each source should be recorded with title, publisher, URL, access date, event time coverage, and whether it is used as an input, validation source, or narrative context.

## Retrospective Run Design

Each case should be replayed in stages:

| Run stage | Data cut-off | Evaluation purpose |
| --- | --- | --- |
| T0 baseline | pre-event baseline only | Check baseline exposure and infrastructure inventory readiness. |
| T1 early hazard | first available forecast or observed hazard layer | Evaluate early screening usefulness. |
| T2 updated hazard | updated hazard extent or official warning footprint | Evaluate improved ranking and infrastructure screening. |
| T3 post-event diagnostic | later validation data | Diagnose errors; do not present as real-time capability. |

Every output folder should preserve:

- run command;
- input file paths and source notes;
- output report and map;
- metadata and uncertainty note;
- evaluation notes.

## Evaluation Questions And Metrics

### 1. Exposure Summary Usefulness

Ask whether the report would have quickly shown:

- where estimated exposed population was concentrated;
- which roads or facilities were potentially affected;
- which administrative units needed review.

Possible metrics:

- number of known affected administrative units appearing in top-k priority areas;
- share of later-reported affected population or locations covered by top-k areas;
- false-positive review burden in top-k areas;
- whether key infrastructure categories were present in outputs.

### 2. Timeliness

Ask whether the system could have generated outputs before or during key response decisions.

Possible metrics:

- time from source data availability to report generation;
- number of manual steps required;
- whether cloud automation could run without local setup;
- whether data licensing or access blocked timely use.

### 3. Prioritization Quality

Ask whether priority rankings would have supported useful review.

Possible metrics:

- top-k recall of later-known hotspots;
- rank movement between T1 and T2;
- comparison of priority ranks to actual response focus areas;
- sensitivity of ranks to weights and missing indicators.

Do not treat response focus as perfect ground truth. Actual response decisions can reflect politics, access, institutional capacity, and information gaps.

### 4. Operational Relevance

Ask whether outputs match real responder questions:

- Which areas may have people exposed?
- Which roads may block access?
- Which facilities may need status checks?
- Where should field verification be prioritized?
- What uncertainty must be communicated?

This can be assessed qualitatively using government actions, rescue reports, and interviews if available.

### 5. Failure Modes

Record where the system fails:

- hazard layer too coarse or late;
- population data outdated;
- OSM roads/facilities incomplete;
- administrative units do not match operational areas;
- no vulnerability or capacity data;
- priority score overreacts to one indicator;
- map/report is not actionable for field teams.

Each failure should become an iteration backlog item, not a hidden limitation.

## Upgrade Loop

After each case:

1. Compare outputs against event evidence.
2. Identify missing data or weak assumptions.
3. Decide whether to improve data adapters, scoring, map/report design, or workflow automation.
4. Re-run the case with the improved version.
5. Document what changed and whether the improvement is real.

Examples of possible upgrades:

- add better hazard ingestion;
- add vulnerability and coping-capacity indicators;
- add access/isolation measures;
- add field-report aggregation;
- add score sensitivity analysis;
- improve validation checklists;
- improve maps for mobile viewing or field handoff.

Avoid overfitting the system to one famous case. Improvements should generalize across cases or be explicitly labeled as context-specific.

## Decision Criteria

The system should be considered promising only if multiple cases show that it can:

- run reproducibly from documented inputs;
- produce outputs faster than manual ad hoc analysis;
- surface relevant exposure or infrastructure concerns;
- support review without making unsupported damage claims;
- communicate uncertainty clearly;
- improve after documented iteration.

If the system only recreates obvious public information slowly, or if its rankings are consistently misleading, the project should iterate before building public-facing reporting tools.

## Ethical Guardrails

- Do not publish individual-level locations.
- Do not treat crowdsourced reports as verified rescue requests without review.
- Do not expose precise sensitive facilities if doing so could create harm.
- Do not claim official allocation recommendations.
- Do not evaluate usefulness only by numerical fit; include uncertainty, privacy, and operational burden.

## Final Technical Report Goal

After several completed case studies, the project should produce a technical report explaining:

- what the system does;
- what cases were tested;
- what data were used;
- where it helped;
- where it failed;
- what iterations improved it;
- what operational conditions are required for responsible use.

The final report should be evidence-based and should not claim validation beyond the cases actually tested.
