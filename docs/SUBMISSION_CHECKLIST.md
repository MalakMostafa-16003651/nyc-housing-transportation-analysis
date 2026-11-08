# Final submission checklist — November 8, 2026

Assessed against the six-person description supplied by the user. The attached
GIU ZIP is a teaching lab, not a separate NYC submission rubric. No additional
report, slide, student-ID, video or single-notebook requirement is inferred.

## Requirement audit

| Requirement | Status and evidence |
| --- | --- |
| Exact housing source `hg8x-zxpr` and transportation source `xeqp-qz8h` | Verified archived official source data, metadata and hashes in `data/raw/`. |
| Required raw/clean dataframe names and shared ZIP, borough, year fields | Implemented in the cleaning notebooks and `scripts/cleaning.py`. Missing source geography is retained or excluded with documented justification. |
| Person 1 / Kareem: housing loading, EDA, missing values, duplicates, outliers, formats, inconsistent values, clean output | Verified `Housing_Data_Cleaning.ipynb`; clean output reproduces the supplied CSV. Valid large values retained, unknown units not invented as zero. |
| Person 1: RQ1 scatter and RQ2 grouped borough bars | Implemented in `Person1_Research_Questions.ipynb` and website. Website RQ2 uses labeled shares with raw totals on hover. Findings are for the matched sample. |
| Person 2 / Youssef: transportation loading, EDA, cleaning, keys, clean output | Verified `Transport_Data_Cleaning.ipynb`. Recovered raw inputs reproduce the supplied clean file. This reconstructed audit workflow does not prove historical authorship. |
| Person 2: RQ3 annual lines and RQ4 project/injury scatter | Implemented in `Person2_Research_Questions.ipynb` and website. |
| Person 3 / Malak: independently aggregate BOTH tables by ZIP + year, then merge | Verified `dataEngP3.ipynb` and canonical `scripts/integration.py`. No direct raw-row merge. |
| Person 3: unmatched rows, duplicates, nulls, types, post-merge cleaning, join rationale | Exact reproduction of 484 unique matched ZIP-years; audit exports and `INTEGRATION_METHOD.md` document exclusions, unknowns and borough conventions. |
| Person 3: RQ5 scatter and RQ6 top-ten relative crash bar | Implemented in integration notebook and website; zero denominators and small-denominator sensitivity disclosed. |
| Person 4 / Ahmed: layout, borough/year/ZIP/housing/transport filters, search, Generate Report, dynamic graphs, integrated-data connection | Verified unit/HTTP and local browser checks. Both measure selectors update the explorer; assigned research questions retain or explicitly label their measures. Generate Report refreshes the on-screen report, not a PDF export. |
| Person 4: RQ7 buildings/injuries scatter and RQ8 borough crash/project bar | Implemented in `RQ7_RQ8_Research_Questions.ipynb` and website. |
| Person 5 / Kenzy: consistent chart styling, titles/labels/legends, main map, findings/limitations/impact | Implemented in `Person5_Research_Questions.ipynb`, shared styling and website story. The map uses approximate source-coordinate positions, not official ZIP boundaries. |
| Person 5: RQ9 overlap map and RQ10 annual comparison | Implemented. RQ10 uses common ZIPs across selected interior years; boundary years and geographic selection are disclosed. |
| Person 6 / Lama: RQ11 categorized scatter and RQ12 borough-colored scatter | Implemented in `Person6_Research_Questions.ipynb` and website; per-matched-year means, thresholds, correlations and limitations documented. |
| Person 6: repository organization, README, member contributions, cleaning/integration documentation, full notebook and website testing | Present; all 29 regression tests and all eight fresh-kernel notebook runs passed in the final audit. Local browser interaction checks passed. |
| Person 6: deploy website and verify live URL | **Verified November 8, 2026:** https://nychousingsafety.pythonanywhere.com/ passed live browser interaction, chart/map and mobile checks. README records the URL. Render remains an optional alternative. |

## What to submit

1. **GitHub repository URL** on the final reviewed branch/main, containing the
   README, six named contributions, requirements files, website source, scripts,
   data provenance, audit evidence and analysis artifacts.
2. **Eight notebooks:** `Housing_Data_Cleaning.ipynb`,
   `Transport_Data_Cleaning.ipynb`, `dataEngP3.ipynb`,
   `Person1_Research_Questions.ipynb`, `Person2_Research_Questions.ipynb`,
   `RQ7_RQ8_Research_Questions.ipynb`, `Person5_Research_Questions.ipynb`,
   `Person6_Research_Questions.ipynb`. Together these contain all twelve assigned
   research questions, visualizations and interpretation.
3. **Data:** archived raw snapshots/metadata/manifest, `df_housing_clean.csv`,
   `df_transport_clean.csv`, `df_housing_agg.csv`, `df_transport_agg.csv`,
   `df_integrated.csv`, map positions and integration audit tables. These are
   included in the repository rather than requiring the grader to retrieve live data.
4. **Public website URL**, after deploying and testing it in a separate browser
   session. Add it to the README and the submission form/report.
5. **Any course-specific extras** only if the actual rubric requires them, such
   as one combined notebook, a written report, slides, a video or a specific ZIP
   upload structure. Confirm these externally; they were not in the supplied brief.

## Verified public deployment

Submit [the live PythonAnywhere website](https://nychousingsafety.pythonanywhere.com/).
Live HTTP, twelve research charts, the map basemap/markers, geographic searches,
both measure selectors, Generate Report, invalid ZIP rejection and mobile layout
were verified November 8, 2026. The deployment requirement is complete for the
tested site. Recheck the URL before submitting, since hosted services can change.

## Optional alternative deployment route

Use the repository's Render Blueprint (`render.yaml`). In Render, create a
Blueprint from this GitHub repository and deploy the selected final branch.
The service installs `requirements.txt` and starts the Dash WSGI entry point with
Gunicorn. The root integrated CSV and map positions must remain in the checkout.
See [Render's official Blueprint documentation](https://render.com/docs/blueprint-spec).
The final audit verified configuration against the documented fields, not an
authenticated Render build or a Linux production run.

After deployment, verify the URL loads, all twelve charts render, map tiles and
markers appear, borough/year/ZIP searches update the report, both measure selectors
work, an invalid ZIP preserves the report with feedback, and empty selections are
handled. Record the URL and date, then replace `LIVE_URL_PENDING` in the README.
These Render instructions are only for an alternative deployment; no Render
connection is required for the existing verified PythonAnywhere service.

## Interpretation that must stay with the submission

The sample excludes unknown ZIPs and unmatched ZIP-years; it is not all NYC
activity. Housing includes preservation and is dated by project starts, not net
growth/completion. Rates per units/projects and median count categories are not
population/traffic-adjusted safety risks. Per-year averaging reduces duration
differences but does not remove selection bias. The analysis is descriptive,
not causal. Keep the existing limitations and assistance provenance in the final files.
