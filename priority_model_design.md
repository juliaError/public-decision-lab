# Priority Model Design

## 1. Purpose

Disaster maps are necessary but not sufficient. A flood extent, cyclone track, fire perimeter, ShakeMap, or other hazard layer can show where a hazard intersects people and assets, but response actors also need action-relevant ways to review where need may be most severe, which lifelines may be disrupted, which road segments may reconnect services, and where follow-up validation should happen first.

Disaster Impact Nowcaster therefore needs priority models that are transparent, configurable, auditable, and locally adaptable. A priority model should help turn existing hazard, exposure, infrastructure, vulnerability, capacity, and future field-report inputs into decision-support rankings. It should also show the components, weights, missing indicators, and uncertainty behind each score.

This framework is decision support, not an official allocation rule. Exposure is not confirmed damage. Priority scores are not truth. Human review, local validation, and institutional accountability are required before operational decisions are made.

The v0.1 scoring framework produces relative within-event ranking indices. A high score means "higher review priority relative to other entities in this event under this configuration." It does not mean absolute humanitarian severity, confirmed damage, or validated caseload. Cross-event comparison requires separate calibration and validation.

## 2. Why a Single Universal Priority Score Is Wrong

Different response actions have different objective functions. A search-and-rescue review may prioritize time criticality, isolation, exposed population, and distress signals. A cash-transfer review may prioritize exposed households, poverty or vulnerability, delivery feasibility, and exclusion risk. A road-repair review may prioritize reconnection benefit relative to repair difficulty. A health-support review may prioritize exposed population, affected health facilities, low alternative access, and medically vulnerable groups.

A single universal score would hide these tradeoffs and could imply that one ranking answers all operational questions. The project should instead support action-specific priority indices, each with explicit indicators, weights, missing-data rules, and interpretation notes.

Each score must also declare its entity level. The baseline flood model uses `admin_area` for need severity, lifeline disruption, rescue review, cash review, and health support, while `road_repair_priority` uses `road_segment`. Mixing entity levels inside one ranked table should be avoided unless the report clearly separates the decision unit.

Raw indicators used by a score should have an entity level compatible with the score entity. Derived scores can be reused only when the producing score has the same entity level. For example, an admin-area rescue score may use an admin-area `need_severity` derived score, but a road-segment repair score should not silently use admin-area indicators.

Examples of action-specific models include:

- rescue priority;
- cash transfers;
- road repair;
- medical support;
- shelter and supplies;
- anticipatory action triggers or review queues.

## 3. Conceptual Foundations

### Disaster risk: hazard, exposure, vulnerability, capacity

UNDRR terminology frames disaster risk as potential loss or harm determined by hazard, exposure, vulnerability, and capacity. Exposure includes people, infrastructure, housing, production capacity, and other assets located in hazard-prone areas. Vulnerability captures physical, social, economic, and environmental susceptibility. Capacity captures the strengths and resources available to manage and reduce risk.

Implication for this project: a priority score should not be based on hazard footprint alone. It should distinguish hazard severity or likelihood, exposed people and assets, vulnerability, and coping capacity.

### INFORM: hazard/exposure, vulnerability, lack of coping capacity

The INFORM Risk methodology uses three high-level dimensions: hazard and exposure, vulnerability, and lack of coping capacity. It is designed for humanitarian risk analysis and makes the dimensions of risk explicit rather than hiding them inside a single opaque number.

Implication for this project: the baseline need-severity model should include hazard or likelihood, exposed population or assets, vulnerability, and lack of coping capacity as separable components.

### JIAF: humanitarian needs severity and intersectoral needs

The Joint Intersectoral Analysis Framework supports people-centered, intersectoral analysis of who is affected, where they are, the combinations of needs they face, and the severity of those needs. JIAF 2.0 materials emphasize contributing factors, interoperable sectoral needs, and intersectoral needs.

Implication for this project: area rankings should support severity review and overlapping needs analysis. A single sector-specific metric should not be presented as a complete humanitarian-needs estimate.

### WMO impact-based forecasting: likelihood and severity of impacts

WMO impact-based forecasting and warning services shift attention from only physical hazards to likely impacts. The operational idea is to communicate actionable information about the likelihood and severity of impacts so people, communities, and governments can prepare and respond.

Implication for this project: future forecast-mode scores should be able to combine likelihood, impact severity, exposure, vulnerability, and uncertainty. The current implementation does not issue warnings.

### Anticipatory action: trigger thresholds and pre-agreed decision rules

Anticipatory action and forecast-based action use risk analysis, forecasts, pre-agreed triggers, and pre-agreed actions to act before or early in a shock. IFRC materials describe funding or actions that can be released when predefined thresholds or triggers are met.

Implication for this project: scores may eventually support trigger review, but v0.1 should not automate action triggers. Thresholds must be locally designed, pre-agreed, reviewed, and documented.

### FEMA Community Lifelines: lifeline stabilization and critical services

FEMA Community Lifelines focus on stabilizing fundamental services after an incident, including safety and security; food, hydration, shelter; health and medical; energy; communications; transportation; hazardous materials; and water systems in the current FEMA construct.

Implication for this project: lifeline disruption should be a distinct score family. The initial data model can support health, transport, and facilities first, then expand to energy, communications, water systems, and other lifeline components when data are available.

### MCDA: transparent multi-criteria prioritization

Multi-criteria decision analysis provides the general logic for transparent multi-dimensional prioritization: define the decision objective, define alternatives, select criteria, normalize indicators, set weights, aggregate, and examine sensitivity. Recent health-emergency MCDA reviews emphasize transparent criteria, stakeholder involvement, weighting, and uncertainty or sensitivity analysis.

Implication for this project: weights must be explicit, configurable, and locally reviewed. Component scores and missing indicators should be reported alongside final scores.

## 4. Core Data Dimensions

### Hazard severity or hazard likelihood

Conceptual meaning: intensity, likelihood, depth, arrival probability, or other hazard-specific measure.

Example variables: flood depth class, inundation probability, cyclone wind speed, fire intensity, earthquake shaking intensity.

Possible sources: external hazard layers, official forecasts, remote-sensing products, national agencies, Copernicus, NASA, USGS, GDACS, Google FloodHub where accessible.

Limitations: hazard timing may not match exposure data; intensity may be uncertain; different products are not directly comparable without calibration.

### Exposed population

Conceptual meaning: estimated people located inside or near the hazard extent.

Example variables: estimated exposed population, exposed households, vulnerable population groups.

Possible sources: local population raster, WorldPop after local download, census grids, official administrative population.

Limitations: population layers may be modeled, outdated, or not time-specific; exposure does not mean confirmed affected persons.

### Exposed assets and infrastructure

Conceptual meaning: roads, facilities, buildings, schools, shelters, hospitals, clinics, and other assets inside the hazard area.

Example variables: road length in hazard, facilities within hazard, buildings exposed, critical facilities exposed.

Possible sources: OSM/HOT exports, local government data, facility registries, road networks.

Limitations: mapping completeness varies; geometry inside a hazard area does not prove damage or service disruption.

### Vulnerability

Conceptual meaning: susceptibility of people, assets, or systems to harm.

Example variables: poverty proxy, age dependency, disability prevalence, informal housing share, chronic disease proxy, marginalized group indicators.

Possible sources: census, household surveys, vulnerability assessments, locally reviewed administrative indicators.

Limitations: vulnerability variables can be sensitive, outdated, or normatively contested. They require local review and privacy safeguards.

### Lack of coping capacity

Conceptual meaning: limited ability of institutions, communities, and systems to manage adverse conditions.

Example variables: emergency service access, health-system density, evacuation capacity, local response capacity, shelter capacity, communications coverage.

Possible sources: administrative capacity datasets, health facility data, road access metrics, local response plans.

Limitations: capacity is difficult to measure; proxies can mislead if used without local context.

### Lifeline disruption

Conceptual meaning: potential disruption to critical services that enable community function.

Example variables: affected health facilities, blocked roads, outage reports, damaged water systems, communications disruption.

Possible sources: infrastructure layers, lifeline operators, field reports, outage feeds, road closure feeds.

Limitations: infrastructure exposure is not the same as service disruption. Operator validation is often required.

### Isolation / access loss

Conceptual meaning: reduced ability to reach populations, facilities, or supply routes.

Example variables: road segments cut, network disconnectivity, travel-time increase, isolated settlements.

Possible sources: road networks, bridge data, routing engines, local access reports.

Limitations: robust isolation analysis needs network topology, passability status, and routing assumptions.

### Field-report intensity, future optional

Conceptual meaning: aggregated reports of distress, need, damage, access barriers, or unmet demand.

Example variables: aggregated distress reports per area, verified needs reports, field assessment severity.

Possible sources: KoBoToolbox, RapidPro, Ushahidi, Sahana, local assessment forms.

Limitations: reports can be biased by access, connectivity, language, and reporting capacity. No personally identifiable data should be used.

### Response feasibility / delivery feasibility

Conceptual meaning: likelihood that an action can be delivered quickly and safely.

Example variables: access status, operational presence, functioning payment channels, warehousing, road passability.

Possible sources: logistics data, partner presence, road network status, payment-provider coverage.

Limitations: feasibility can change quickly and may include sensitive operational information. Feasibility is not need. If feasibility is blended into a priority score without care, assistance can become biased toward easy-to-reach areas even when harder-to-reach areas have greater humanitarian need.

### Response cost or difficulty

Conceptual meaning: expected cost, time, technical difficulty, or risk of implementing an action.

Example variables: repair difficulty, segment length, bridge status, terrain, procurement time, security constraints.

Possible sources: engineering assessments, road inventory, logistics plans, local authorities.

Limitations: early estimates can be rough; cost terms should not be hidden or treated as precise.

### Data quality and uncertainty

Conceptual meaning: confidence in the indicators used for scoring.

Example variables: data age, completeness, source type, spatial resolution, missing indicators, validation status.

Possible sources: metadata files, source documentation, data-source adapters, validation logs.

Limitations: uncertainty is often qualitative. It should be reported, not buried.

## 5. Score Families

### 5.1 Need Severity Score

Purpose: estimate where humanitarian need is likely to be most severe.

Suggested conceptual structure:

```text
need_severity_i =
  f(hazard_severity_i, exposed_population_i, vulnerability_i, lack_of_coping_capacity_i)
```

The first implementation supports a configurable weighted additive form:

```text
need_severity_i =
  w_hazard * H_i
+ w_exposure * E_i
+ w_vulnerability * V_i
+ w_capacity * C_i
```

Where:

- `H_i` is hazard severity or likelihood.
- `E_i` is exposed population or assets.
- `V_i` is vulnerability.
- `C_i` is lack of coping capacity.

Weights are illustrative unless locally reviewed. The output is a review index, not a verified humanitarian-needs classification.

### 5.2 Lifeline Disruption Score

Purpose: estimate potential disruption to critical services.

Suggested dimensions:

- health and medical;
- transportation;
- energy, future optional;
- communications, future optional;
- food, water, and shelter, future optional;
- schools and shelters, where relevant.

Initial implementation may only support health, transport, and facility-based indicators because those are the current local-file inputs.

### 5.3 Rescue Priority Score

Purpose: support area-level review for urgent life-saving or search-and-rescue triage.

Suggested dimensions:

- need severity;
- time criticality;
- isolation;
- field distress signals;
- exposed population;
- vulnerable population.

This is not individual rescue dispatch. It must not use identifiable personal data and must not be presented as an official rescue order.

### 5.4 Cash Transfer Priority Score

Purpose: identify areas where emergency cash or voucher support may be urgent.

Suggested dimensions:

- exposed households;
- poverty or vulnerability;
- livelihood disruption proxy;
- delivery feasibility;
- exclusion risk.

This is a targeting-support index, not a final beneficiary list. Cash targeting requires program rules, consent, protection review, local validation, and complaints or appeals mechanisms.

The baseline implementation separates:

- `cash_need_score`: exposure, vulnerability, and livelihood-disruption review;
- `cash_feasibility_score`: operational delivery feasibility, reported separately;
- `cash_priority`: a review score that follows need and carries feasibility as a component and warning.

Delivery feasibility must not silently suppress humanitarian need. If users want to combine need and feasibility for an operational workplan, that choice should be made explicitly in a local config and documented in the report.

### 5.5 Road Repair Priority Score

Purpose: rank road segments or corridors for repair review.

Suggested structure:

```text
road_repair_priority_s =
  benefit_s / cost_or_difficulty_s
```

Benefit can include:

- population reconnected;
- hospitals reconnected;
- schools or shelters reconnected;
- aid-route importance;
- reduction in travel time or isolation.

Cost or difficulty can include repair difficulty, segment length, bridge status, terrain, or safety constraints. The v0.1 implementation uses a stable normalized benefit-over-cost index, not an engineering repair estimate.

The baseline implementation keeps:

- `road_repair_priority_benefit_index`;
- `road_repair_priority_cost_index`;
- `road_repair_priority_epsilon`;
- final `road_repair_priority`.

The formula is:

```text
road_repair_priority_s =
  benefit_index_s / (epsilon + cost_index_s)
```

`epsilon` prevents division by zero. Equal or zero-valued cost indicators contribute no within-event cost ranking information; they do not prove repair cost is actually zero. Cost assumptions should remain visible in outputs and reports.

### 5.6 Health Support Priority Score

Purpose: identify areas where medical support may be most urgent.

Suggested dimensions:

- exposed population;
- affected health facilities;
- low alternative access;
- vulnerable population;
- road isolation;
- field medical-need reports, future optional.

This score should be validated against health-cluster or local health authority information before operational use.

## 6. Normalization and Aggregation

Default normalization options:

- min-max normalization within event;
- percentile rank;
- z-score, optional;
- binary threshold indicators;
- robust scaling, optional.

The v0.1 implementation uses min-max normalization within event. If all non-missing values of an indicator are equal, the implementation returns `0.0` under the `zero_discriminatory_contribution` policy. This means the indicator provides no within-event ranking information. It does not mean the underlying risk, need, cost, or benefit is zero.

Each indicator in the YAML catalog declares a direction:

- `higher_is_worse`;
- `higher_is_better`;
- `higher_is_costlier`;
- `lower_is_worse`.

Direction metadata tells the scoring code how to orient normalized values. For example, lower access may be worse, while higher reconnection benefit is better and higher repair difficulty is costlier.

Optional missing indicators use `renormalize_available_and_flag` in the baseline model. This means absent optional indicators are flagged, and available indicator weights are renormalized so a missing optional input does not mechanically lower the score. Missing required indicators remain explicit and can block row-level score computation.

Component columns use normalized indicator values multiplied by their original configured weights. Final score columns may renormalize by row-level available weights when optional indicators are missing. Reports should show both component columns and the row-level available weight denominator where feasible.

Warnings:

- within-event normalization affects comparability across events;
- cross-event comparability requires separate calibration;
- missing data must be explicit;
- component scores should be included in machine-readable outputs where feasible.

## 7. Weighting Strategy

Weights must be:

- stored in YAML config files;
- explicit;
- editable by users;
- documented in reports;
- never hidden inside code.

Default baseline weights for v0.1 are illustrative settings only. They exist so users can run tests and demos, not because they are validated for any country, event, or organization.

The default weights are not empirical estimates, universal norms, or evidence that one dimension is more important in all settings. They are placeholders for a transparent runnable model and must be replaced or reviewed for local operational use.

The local-context override mechanism should be a user-supplied YAML file with the same schema as `configs/priority_models/baseline_flood.yml`. Action-specific weights should be reviewed separately for need severity, lifeline disruption, rescue review, cash support, health support, and road repair.

Sensitivity-analysis plan:

- vary one weight at a time within locally agreed ranges;
- compare rank stability;
- report areas whose ranks are highly sensitive to weights;
- document stakeholder review of criteria and weights;
- avoid operational use when results are unstable and stakes are high.

## 8. Trigger and Threshold Logic

Scores could eventually support trigger review for:

- early warning;
- anticipatory action;
- urgent review;
- manual validation;
- escalation.

Do not implement fully automated action triggers yet. Future trigger logic should require a pre-agreed action plan, defined thresholds, source-quality rules, validation steps, and a human approval path. Trigger outputs should say "review threshold reached" rather than "action authorized" unless an accountable institution has explicitly adopted that rule.

## 9. Data Quality and Uncertainty

Every score should carry or link to:

- data completeness;
- data age;
- spatial resolution;
- source type;
- missing indicators;
- uncertainty notes.

The v0.1 data-quality flag uses:

- `high`: required and optional indicators are present;
- `medium`: required indicators are present but optional indicators are missing;
- `low`: some required indicators are missing;
- `insufficient`: all required indicators are missing.

Required missing indicators should block score computation unless an explicit local rule says otherwise. Optional missing indicators may be skipped with flags.

The implementation also separates `model_completeness_flag` from `data_quality_flag`:

- `data_quality_flag` summarizes whether the row has enough observed input values for the score;
- `model_completeness_flag` identifies whether the configured model was complete, optional indicators were missing, required indicators were missing, or the score was insufficient.

The v0.1 `data_quality_flag` is still a completeness-based proxy. It is not a full assessment of data age, source reliability, spatial resolution, uncertainty, or validation status.

Optional missing values should not imply low humanitarian need. They indicate that the model is less complete for that row or score family.

## 10. Ethical Safeguards

Priority scoring must follow these safeguards:

- no individual tracking;
- no personally identifiable data;
- no automatic official allocation decisions;
- no publication of sensitive locations if doing so could increase risk;
- distinguish exposure from damage;
- local validation required;
- document uncertainty and normative choices;
- show weights and components where feasible;
- include a path for review, correction, and appeal when scores affect assistance.

## 11. v0.1 Implementation Plan

v0.1 should implement:

- config-driven scoring;
- score-level entity metadata;
- indicator catalog with concept, entity level, direction, role, units, interpretation notes, and sensitivity or privacy notes;
- area-level need severity score;
- area-level lifeline disruption score;
- area-level rescue priority score;
- separate area-level cash need score, cash feasibility score, and cash priority review score;
- area-level health support priority score;
- basic road repair score if road-segment data exist;
- min-max normalization within event;
- zero discriminatory contribution for equal-value indicators;
- optional-missing renormalization with flags;
- component columns for transparent weighted scores;
- missing-indicator flags;
- data-quality flags;
- model-completeness flags;
- config validation for weights, indicators, directions, entity levels, and formula names;
- no live field reports yet;
- no personal data;
- no automatic triggers.

## 12. Future Roadmap

v0.2 to v1.0 should consider:

- field reports with aggregation and privacy safeguards;
- mobility aggregates, only when privacy-preserving and legally appropriate;
- historical calibration and validation against official reports;
- sensitivity analysis and rank-stability outputs;
- multi-hazard expansion;
- local stakeholder weight elicitation;
- dashboard display;
- richer report templates;
- configurable trigger-review rules;
- interoperability with humanitarian assessment workflows.

## Reference Anchors

Verified web references used for this design:

- UNDRR Terminology: Disaster risk, Exposure, Vulnerability, and Capacity.
  - https://www.undrr.org/terminology/disaster-risk
  - https://www.undrr.org/terminology/exposure
  - https://www.undrr.org/terminology/vulnerability
  - https://www.undrr.org/terminology/capacity
- INFORM Risk methodology:
  - https://drmkc.jrc.ec.europa.eu/inform-index/INFORM-Risk/Methodology
- JIAF overview and JIAF 2.0 pointers:
  - https://sdgintegration.undp.org/joint-intersectoral-analysis-framework
  - https://www.cccmcluster.org/resources/coordinator-toolkit/hnos
- WMO impact-based forecasting and warning services:
  - https://wmo.int/impact-based-forecast-and-warning-services
- IFRC early warning, anticipatory action, and Anticipatory Pillar of DREF:
  - https://www.ifrc.org/early-warning-early-action
  - https://www.ifrc.org/happening-now/emergencies/anticipatory-pillar-dref
- FEMA Community Lifelines:
  - https://www.fema.gov/af/emergency-managers/practitioners/lifelines
- MCDA in health-emergency decision support:
  - https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2025.1584026

References should be re-checked before publication-quality citation formatting or operational adoption.
