# Project audit and requirements review

Reviewed against the team's supplied brief on **November 7, 2026**. The attached
GIU ZIP is a data-integration teaching lab using retail and jobs datasets. Its
examples were treated as reference material, not instructions to change this NYC
project or to run its API/LLM examples. No separate NYC grading rubric was present.

## Deliverables for Persons 1–5

| Person | Requirements | Repository evidence after repair |
| --- | --- | --- |
| 1 — Kareem | Housing loading, EDA, missing/duplicate/outlier/type/value checks; standardized keys; cleaned data; two charts | `Housing_Data_Cleaning.ipynb`, archived raw housing, `scripts/cleaning.py`, `df_housing_clean.csv`, `Person1_Research_Questions.ipynb`, website RQ1/RQ2. Offline source reproduction added; source observations and labels corrected. |
| 2 — Youssef | SIRTA loading, EDA, cleaning, standardized keys, cleaned data, two charts | `Transport_Data_Cleaning.ipynb`, archived raw SIRTA, `scripts/cleaning.py`, `df_transport_clean.csv`, `Person2_Research_Questions.ipynb`, website RQ3/RQ4. Original cleaning notebook was missing; this audit reconstructed a method reproducing every supplied source field. This is an audit addition, not proof of Youssef's original process. |
| 3 — Malak | Aggregate both tables by ZIP/year first; merge; audit unmatched/duplicate/null/type issues; post-clean; explain join; two charts | `dataEngP3.ipynb`, shared `scripts/integration.py`, both aggregate CSVs, `df_integrated.csv`, audit tables, `INTEGRATION_METHOD.md`, RQ5/RQ6. Existing integrated values reproduced unchanged. |
| 4 — Ahmed | Layout; borough/year/ZIP/housing/transport filters; search; Generate Report; graphs connected to integrated data; two charts | `app/`, `RQ7_RQ8_Research_Questions.ipynb`, RQ7/RQ8. Search validation, real-data loading and edge cases repaired. An additional selected-measures explorer responds to both measure selectors while fixed RQs preserve their meanings. |
| 5 — Kenzy | Consistent chart titles/labels/legends; main map; evidence-based findings/limits/impact; two charts | `Person5_Research_Questions.ipynb`, RQ9/RQ10, `data/zip_centroids.csv`, shared chart styling and dashboard story. Removed unsupported causal claims and changed the main annual comparison to a balanced ZIP panel. |

Names and assignments are user-provided. We reviewed the work, not individual
authorship. The transportation reconstruction and repair assistance should remain
identified in the contribution record.

## Material findings

- All three supplied cleaned/integrated CSVs match the repository values. Line
  ending differences are not data changes.
- Recovered official raw housing has 9,551 rows/41 columns; its cleaning reproduces
  9,551 rows/42 columns. There are 1,958 missing housing ZIPs and 29 unknown
  affordable-unit values; unknowns are not proof of zero production.
- Raw SIRTA has 13,754 rows. The supplied 8,072-row clean file is the source subset
  with ZIPs. The 5,682 excluded rows include three exact duplicates; dropping the
  duplicates first then missing ZIPs gives the same retained file. All retained
  crash IDs are distinct. Source ZIP10000 occurs in 44 retained rows and requires
  geography review; none matches housing, so none enters the integrated data.
- Malak's aggregation order is correct. The 1,155 housing and 829 transport groups
  produce 484 matches; 1,016 unmatched groups are exported. The final 484 rows
  cover 143 ZIPs and have no duplicate ZIP/year keys or null output values.
- Six matched borough disagreements are retained in an audit table and resolved
  using the existing housing-majority convention. Geography was not independently
  certified against ZIP boundaries.
- The map's saved positions average source coordinates; they are approximate
  positions, not official ZIP centroids. Missing coordinates are disclosed.
- Calendar coverage and matching differ by year. 2022's October start in the
  cleaned transportation table comes from ZIP availability; the raw source starts
  earlier. Calling 2023–2025 interior calendar years does not imply complete
  geography or complete crash coverage.
- For the 72 ZIPs matched in every year of 2023–2025, affordable units decrease
  from 25,494 to 21,562 (-15.4%), while severe injuries increase from 1,177 to
  1,453 (+23.4%). This replaces the previous changing-sample, incorrectly
  citywide 'flat housing' story. It does not establish the effect of housing on
  injuries. The within-ZIP analysis is descriptive, without an independence-based
  p-value for repeated ZIP observations.

Read [INTEGRATION_METHOD.md](INTEGRATION_METHOD.md) for aggregation definitions,
unknown-unit handling, join decisions and reproducibility commands. Do not convert
missing source geography or unmatched records to zero counts without justification.

## Validation

Run from the repository root after installing `requirements-analysis.txt`:

```bash
python -m unittest discover -s tests -v
python scripts/integration.py
python scripts/check_notebooks.py
```

The notebook checker verifies raw SHA-256 hashes, copies the source/data/modules
into an isolated temporary directory, and executes all eight notebooks with fresh
kernels. Optional `--write-executed` refreshes checked-in notebook outputs and four
static figures only after all notebooks pass; it does not replace source CSVs.
The regression suite checks actual data, independent aggregation, source cleaning,
invalid inputs, filters/search, report HTTP callbacks, map/trend edge cases and
all 16 measure combinations. Final run results are recorded in `VERIFICATION.md`.

## Person 6 deliverables (November 8, 2026)

RQ11 and RQ12 are implemented in `app/charts/rq11_rq12.py` and analysed in
`Person6_Research_Questions.ipynb`. Both compare ZIPs per matched year, because
summed totals correlate strongly with how many years a ZIP is matched (Spearman
0.76 units, 0.80 crashes). This also means summed-total correlations elsewhere
(RQ1, RQ4, RQ7) partly reflect coverage; RQ12 reports the per-year association
(ρ = 0.30 citywide; clear only in the Bronx). The notebook checks that the website
functions reproduce its values. Four regression tests cover RQ11/RQ12, including a
zero-median edge case and empty selections. `render.yaml` defines the Render
deployment; the live URL is recorded in the README once deployed and tested.

## Contribution and handoff

The README lists all six supplied names and assignments, with Malak responsible for
integration. `AI_PROMPTS.md` preserves the prior repository's prompt record; this
audit did not independently authenticate its historical attribution. Keep member
confirmation and any additional disclosure required by the course with the final
submission. A single assembled notebook was not required by the supplied brief;
the documented run order and fresh execution cover the separate deliverables.

Repairs are prepared on `codex/project-audit-persons-1-5`. Review source changes,
run the checks above, then merge the reviewed branch. The integrated values were
preserved; audit files, reproducible raw inputs and corrected figures accompany
the code and documentation.


## Final six-person recheck (November 8, 2026)

All 29 regression tests and all eight notebooks (86 code cells) passed. RQ11/RQ12 are present and tested; they are no longer pending. Local browser checks passed. Public deployment remains unverified; a Render configuration is not a live URL. See SUBMISSION_CHECKLIST.md for the requirement matrix and submission contents. The Persons 1–5 repair PR was already merged; this follow-up documents the completed six-person codebase.
