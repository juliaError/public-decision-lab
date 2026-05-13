# pk_sindh_khairpur_flood_2022 Evaluation

## Current Judgment

Status: insufficient_evidence

This case is a better next candidate than Zhengzhou for the first full historical run because it has a public, machine-readable UNOSAT flood-water vector source. However, a complete v0.1 replay has not yet been run because the hazard package is large and still needs external download, extraction, and conversion.

## What Improved In This Iteration

- The process no longer stops at the Zhengzhou hazard-data gap.
- A second historical case has been selected using a concrete public hazard source.
- The exact machine-readable hazard package, exposure workbook, and source limitations are now registered.
- The repository now has an output checker so future case runs can be mechanically checked for the seven core artifacts.

## Exposure Summary Usefulness

Not evaluated yet. The system must first run against the converted UNOSAT hazard polygon and local OSM/admin inputs.

Diagnostic comparison target:

- Compare admin-level outputs against the UNOSAT district-level exposure workbook.
- Do not expect exact agreement unless the same population grid, admin units, and buffer/intersection logic are used.
- Treat differences as a diagnostic prompt, not automatic evidence that either source is wrong.

## Priority Ranking Review

Not evaluated yet.

Questions for the first completed run:

- Do top-ranked admin units include districts with high UNOSAT potentially exposed population?
- Do outputs identify roads and facilities that would have merited status checks?
- Do rankings change substantially if population is unavailable?
- Does the report make uncertainty clear enough for non-technical users?

## Infrastructure And Access

Not evaluated yet.

Known issue:

- OSM roads and facilities need a date-aware or at least source-documented export.
- Facility completeness may be uneven and should not be interpreted as verified service availability.

## Failure Modes Already Identified

- Large hazard vector packages may slow down ad hoc local iteration.
- HDX preview layers were not directly accessible as simple GeoJSON through the attempted WFS URLs.
- The v0.1 pipeline cannot use UNOSAT's exposure workbook as a population raster.
- Without local population input, the first run will focus on infrastructure exposure and admin review rather than independently estimated exposed population.

## Upgrade Backlog

1. Add documented external-data preparation steps for large UNOSAT/HDX shapefile packages.
2. Add a small conversion helper that extracts the flood-water layer from a local ZIP or extracted shapefile and writes pipeline-ready GeoJSON.
3. Add a case-run command that reads a manifest stage and runs the core CLI when all local paths exist.
4. Add comparison tooling for external validation tables such as UNOSAT district-level exposure workbooks.
5. Re-run this case after the converted hazard and local OSM/admin inputs exist.

## Usefulness Judgment

Not enough evidence yet. This case should continue as the first non-China historical replay candidate because it has a defensible hazard source and clear validation material.
