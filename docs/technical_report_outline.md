# Technical Report Outline

## Working Title

Disaster Impact Nowcaster: Retrospective Case Evaluation Of A Lightweight Exposure And Priority-Review System

## Executive Summary

Summarize:

- what the system does;
- what cases were tested;
- whether the system was useful;
- where it failed;
- what upgrades were required;
- how it should and should not be used.

Do not claim the system is validated beyond the evidence in the case studies.

## 1. Motivation

Explain the practical problem:

- disaster maps alone are not enough;
- public and local actors need fast, transparent summaries;
- early response needs exposure, infrastructure, and priority-review outputs;
- outputs must avoid overclaiming confirmed damage or official allocation.

## 2. System Overview

Describe the architecture:

- event or AOI;
- hazard layer;
- population and infrastructure layers;
- exposure summary;
- priority table;
- report, map, metadata, and uncertainty note;
- optional cloud workflow.

Include a diagram of the data flow.

## 3. Scope And Non-Goals

State clearly:

- the system is an integration and decision-support layer;
- it does not forecast hazards from scratch;
- it does not replace official agencies;
- it does not identify victims;
- it does not confirm damage;
- it does not automatically allocate rescue or aid.

## 4. Methods

### 4.1 Inputs

Describe:

- hazard data;
- population data;
- roads and facilities;
- administrative boundaries;
- optional vulnerability, capacity, or field-report indicators.

### 4.2 Exposure Estimation

Explain the intersection-based and raster-clipping methods used in the evaluated version.

### 4.3 Priority Scoring

Describe the configurable, action-specific scoring approach:

- need severity;
- lifeline disruption;
- rescue review;
- cash-transfer support;
- health support;
- road repair review.

Emphasize that weights are illustrative unless locally reviewed.

### 4.4 Cloud Reproducibility

Describe the GitHub Actions demo and future automation path.

### 4.5 Retrospective Evaluation Design

Explain:

- case selection;
- data cut-offs;
- real-time simulation vs post-event diagnostic analysis;
- source collection;
- comparison metrics;
- qualitative usefulness review.

## 5. Case Studies

Each case should use the same structure:

1. event summary;
2. data sources;
3. run setup;
4. output summary;
5. comparison with public evidence;
6. what helped;
7. what failed;
8. upgrade decisions.

Candidate cases:

- 2021 Henan / Zhengzhou extreme rainfall and flooding;
- 2023 Beijing-Tianjin-Hebei / Haihe Basin flooding after Typhoon Doksuri;
- 2022 Pakistan floods;
- 2023 Libya Derna flooding.

The final report should include only cases that have enough evidence and reproducible runs.

## 6. Cross-Case Findings

Compare:

- where exposure screening was useful;
- where road/facility outputs helped;
- whether priority rankings matched later-known hotspots;
- what errors repeated across cases;
- how much manual effort was saved;
- what remained impossible without better data.

## 7. Iterations And Upgrades

Document each upgrade:

- problem found;
- change made;
- case re-run;
- whether the change improved outputs;
- whether the improvement generalized beyond one case.

Possible upgrade categories:

- hazard ingestion;
- population and vulnerability indicators;
- access/isolation modeling;
- facility classification;
- field-report aggregation;
- score sensitivity analysis;
- map/report design;
- cloud automation.

## 8. Responsible Use

Discuss:

- exposure vs confirmed damage;
- privacy and sensitive locations;
- public communication risks;
- human review;
- local validation;
- limits of crowdsourced or self-reported data.

If the report discusses a future WeChat Mini Program, it should state that exact user locations require explicit consent, strict access control, minimization, retention limits, and review workflows.

## 9. Recommendations

Separate recommendations by audience:

- public-interest technologists;
- local governments and emergency managers;
- humanitarian or civil-society users;
- researchers;
- future product builders.

Each recommendation should say what the system can support now and what must be validated first.

## 10. Conclusion

State the evidence-based conclusion:

- useful where evidence supports usefulness;
- not useful or not ready where evidence shows gaps;
- next required upgrades before operational use.

## Appendices

- case source tables;
- run commands;
- configuration files;
- score weights and sensitivity checks;
- generated report examples;
- validation checklists;
- known limitations.
