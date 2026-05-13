# cn_henan_zhengzhou_flood_2021 Case Note

## Case Summary

This case covers the July 2021 extreme rainfall and flooding disaster in Henan, with a focus on Zhengzhou and surrounding affected areas. It is selected because public post-event investigation material and event-time response reporting are available, and because the event is highly relevant for evaluating a future China-facing disaster exposure and reporting tool.

This note does not evaluate system performance yet. The case is currently marked `data_gap` because a trustworthy event-time or updated flood polygon has not yet been identified for a reproducible nowcaster run.

## Evaluation Purpose

This case should test whether Disaster Impact Nowcaster can eventually support:

- urban flood exposure screening;
- road and transport disruption review;
- facility status-check prioritization;
- admin-area priority review;
- cautious report language around uncertainty and validation.

## What Can Be Used As Event-Time Evidence

The event-time source set currently includes:

- emergency response activation reporting from 2021-07-20;
- cross-regional rescue deployment reporting from 2021-07-21;
- rescue coordination notice from 2021-07-21;
- provincial response and recovery reporting from 2021-07-23.

These can help reconstruct what response actors publicly reported during the event. They do not provide a complete hazard extent.

## What Is Post-Event Evidence

The State Council investigation release and related Q&A are post-event sources from 2022-01-21. They may be used to validate, interpret, and diagnose the case, but they must not be treated as information the system would have known during the event.

## Data Availability

Current status:

- AOI: not yet prepared;
- hazard extent: data gap;
- admin boundaries: not yet prepared;
- population grid: not yet prepared;
- roads: not yet prepared;
- facilities: not yet prepared.

The core pipeline requires a hazard polygon. Until a credible flood extent or clearly labeled proxy is prepared, the case should not claim a successful nowcaster run.

## Data Gap

The most important current blocker is hazard representation. Rainfall, warning polygons, administrative impact lists, and media-described affected places may be useful context, but they are not the same as observed inundation.

If a proxy is later used, it must be labeled as a proxy hazard and evaluated separately from a true observed flood extent.

## Non-Claims

- No model output identifies confirmed victims.
- No exposure output confirms damage.
- No priority output is an official rescue or allocation rule.
- No post-event finding should be presented as real-time system knowledge.

## Next Steps

1. Search for a credible flood extent, rapid mapping product, or reproducible proxy layer.
2. Prepare AOI, admin, population, roads, and facility inputs without committing large raw data.
3. Run T1 only if event-time hazard input is available.
4. Run T3 diagnostic only after clearly separating post-event validation evidence.
