# pk_sindh_khairpur_flood_2022 Sources

This case was selected after the Zhengzhou case reached a hazard-data gap. The goal is to keep the retrospective evaluation moving with a case that has public UNOSAT/HDX machine-readable flood-water resources. The data still need local download, extraction, and conversion before a full `disaster-nowcaster run` can be claimed.

| Source ID | Title | Publisher | URL/path | Access date | Availability | Role | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unosat_hdx_khairpur_water_extent_20220907 | Satellite detected water extent in Khairpur Nathan Shah Town, Sindh Province, Pakistan as of 31 August 2022 | United Nations Satellite Centre (UNOSAT) / Humanitarian Data Exchange | https://data.humdata.org/dataset/f858d69f-481b-49b6-bcfa-1c2dc74dd346 | 2026-05-14 | post_event | input | Machine-readable source exists. The zipped shapefile is about 286 MB, so it must stay outside the repository. |
| unosat_khairpur_map_pdf_20220905 | UNOSAT map: Satellite detected water extent in Khairpur Nathan Shah Town | United Nations Satellite Centre (UNOSAT) | https://unosat.org/static/unosat_filesystem/3349/UNOSAT_A3_Natural_Landscape_FL20220808PAK_Sindh_31Aug2022_v2.pdf | 2026-05-14 | post_event | validation | Map context and cautious interpretation notes. Not a substitute for vector hazard input. |
| unosat_population_exposure_xlsx_20220907 | UNOSAT Population Exposure FL20220808PAK 31 Aug 2022 Sindh | United Nations Satellite Centre (UNOSAT) | https://unosat.org/static/unosat_filesystem/3349/UNOSAT_Population_Exposure_FL20220808PAK_31Aug2022_Sindh.xlsx | 2026-05-14 | post_event | validation | Small district-level exposure table. It is not a population raster input. |
| un_pakistan_flood_response_plan_20220902 | 2022 Pakistan Floods Response Plan | United Nations in Pakistan | https://pakistan.un.org/en/197499-2022-pakistan-floods-response-plan-frp | 2026-05-14 | during_event | response_timeline | Response planning context available near the event period. |
| unicef_pakistan_sitrep_20220909 | Pakistan Humanitarian Situation Report No. 2 (Floods), September 2022 | UNICEF | https://www.unicef.org/documents/pakistan-humanitarian-situation-report-no2-floods-september-2022 | 2026-05-14 | during_event | response_timeline | Humanitarian situation context near the UNOSAT product publication window. |
| hot_osm_pakistan_flood_2022 | Pakistan Flood 2022 | OpenStreetMap Wiki / HOT context | https://wiki.openstreetmap.org/wiki/Pakistan_Flood_2022 | 2026-05-14 | during_event | context | Mapping response context. OSM infrastructure extracts still need to be downloaded and checked. |

## Source Use Rules

- The UNOSAT vector package can become a hazard input only after it is downloaded outside the repository and converted to the GeoJSON expected by the v0.1 CLI.
- The UNOSAT PDF and population-exposure workbook are validation/context sources, not substitute inputs for the core pipeline.
- During-event sources may be used to reconstruct what responders plausibly knew at the time.
- Post-event sources may be used for diagnosis, but must not be mixed into T1/T2 real-time simulation claims.
- All outputs must use cautious language: estimated exposed population, potentially affected infrastructure, not confirmed damage, and requires validation.
