# cn_henan_zhengzhou_flood_2021 Evaluation

## Status

Current usefulness judgment: `insufficient_evidence`.

The case has not yet been run through Disaster Impact Nowcaster because a credible hazard extent has not been prepared. This is a data gap, not evidence that the system is useful or not useful.

## Exposure Summary Usefulness

Not evaluated yet.

Questions to answer after a run:

- Would the report have identified administrative areas requiring early review?
- Would estimated exposed population have been concentrated in places later described as heavily affected?
- Would the output have helped separate broad situational awareness from confirmed damage claims?

## Priority Ranking Review

Not evaluated yet.

Questions to answer after a run:

- Did top-k priority areas overlap later-known response focus areas?
- Were rankings driven by real exposure, infrastructure density, data gaps, or arbitrary weighting?
- Did missing vulnerability, capacity, or underground-infrastructure indicators limit usefulness?

## Infrastructure And Access

Not evaluated yet.

This case may require special attention to:

- urban road underpasses and tunnels;
- metro or underground transport exposure;
- hospital power and access constraints;
- shelter and evacuation access;
- incomplete OSM or facility inventories.

## Timeliness

Not evaluated yet.

The eventual T1 evaluation should ask whether a report could have been produced before or during the 2021-07-20 emergency response window using only data available at that time.

## Failure Modes Already Identified

| Failure mode | Evidence status | Upgrade implication |
| --- | --- | --- |
| No verified flood extent prepared | Known data gap | Search official rapid mapping or use a clearly labeled proxy only for diagnostic work. |
| Urban underground infrastructure not represented | Plausible model gap | Consider optional critical transport/tunnel/metro facility inventory. |
| Post-event findings could leak into real-time simulation | Method risk | Keep T1/T2 and T3 evidence strictly separated. |

## Upgrade Backlog

| Issue found | Proposed upgrade | Priority | Owner/status |
| --- | --- | --- | --- |
| Missing hazard extent | Identify a credible flood extent or clearly documented proxy hazard layer. | high | open |
| Underground and tunnel risks not modeled | Add optional urban critical-transport inventory and report limitations. | medium | open |
| Evaluation may overfit to one case | Compare against at least one other China case and one international case. | medium | open |

## Technical Report Notes

Potential report lesson, pending actual runs:

- This case may test whether a lightweight nowcasting layer can help organize early review questions even when post-event investigation later shows much richer causal detail.
- The case should not be used to claim the system would have prevented losses or replaced official emergency management.
