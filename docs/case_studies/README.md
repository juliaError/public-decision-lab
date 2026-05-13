# Case Studies

This folder is for retrospective disaster case studies. Each case should test whether Disaster Impact Nowcaster could have provided useful exposure screening, priority review, or operational context during a past event.

Case studies must not claim confirmed damage from model outputs. They should compare system outputs with traceable public evidence and clearly separate:

- data available during the event;
- data discovered after the event;
- system outputs;
- evaluation judgments;
- upgrade decisions.

## Recommended Folder Structure

```text
docs/case_studies/
├── README.md
├── case_template.md
└── <case_id>/
    ├── case_note.md
    ├── sources.md
    ├── run_log.md
    └── evaluation.md
```

Large raw data should not be committed. Store large rasters, downloaded satellite products, and bulky administrative files outside the repository. The case note should record where they can be obtained and how they were used.

## Case Status Labels

Use these labels consistently:

- `candidate`: plausible case, sources not fully reviewed;
- `source_review`: source collection in progress;
- `data_ready`: inputs identified and reproducible run is possible;
- `run_complete`: at least one nowcaster run completed;
- `evaluated`: outputs compared against evidence;
- `iteration_needed`: results show a concrete upgrade is needed;
- `report_ready`: case can be included in the technical report.

## Minimum Evidence Standard

A case should not be marked `evaluated` until it has:

- at least one hazard or event-footprint source;
- at least one public source describing response actions or impacts;
- a reproducible run command;
- an uncertainty note;
- a comparison between outputs and external evidence;
- a clear statement of whether the system helped, failed, or needs more data.
