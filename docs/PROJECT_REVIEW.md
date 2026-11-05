# Integration review and team handoff

## Why the questions were missing

The main checkout contained Member 1's completed research notebook and PNGs,
but `app/charts/rq1_rq2.py` still returned placeholder figures. RQ3/RQ4 were also
placeholders. Notebook cells do not run when Dash starts: website chart functions
must explicitly implement their plots and be registered in `ALL_CHARTS`.

RQ1–RQ4 now use the same integrated CSV as RQ5–RQ8. RQ1/RQ2 adapt Member 1's
analysis; RQ3/RQ4 implement the team's supplied questions. They are not evidence
that Member 2's missing notebook or cleaning work has been reviewed.

## Requirements checked against the supplied project description

| Area | Evidence / remaining work |
| --- | --- |
| Housing cleaning | `Housing_Data_Cleaning.ipynb` and cleaned CSV present; final Colab download is now optional for local Jupyter. Live source download has not been revalidated. |
| Transportation cleaning | Cleaned CSV present; original transportation loading, EDA and cleaning notebook absent from this main checkout. RQ3/RQ4 analysis has been added in `Person2_Research_Questions.ipynb`. Ask Member 2 to merge the source notebook, with explanations and dataset link. |
| Integration | `dataEngP3.ipynb` aggregates each dataset by ZIP + year before a validated one-to-one merge. It audits an outer join, then retains matched rows only. |
| Scope of results | Integrated data represents matched ZIP-years, not all NYC housing or all crashes. Unmatched records are excluded, not zero-filled. Summed annual project counts are not necessarily unique projects across years. |
| RQ1–RQ8 website | Implemented. Borough, ZIP and year filters apply. Fixed research questions retain their own metrics; RQ8 follows the transport selector. |
| RQ9–RQ12 | Still placeholders: Members 5 and 6 must supply their questions, charts and analysis. Six members require 12 visualizations. |
| Story | Website story text still needs Members 5/6's final synthesis. |
| Final notebook | Separate notebooks exist; assemble a documented, restart-and-run-all submission covering both source datasets, cleaning, integration, all research questions and prompts used. Do not merely concatenate saved outputs. |
| Deployment | Gunicorn entry point is available; no live deployed URL was verified. |
| Contribution record | README currently documents Members 1 and 4. Add actual names/IDs and evidence for all six; do not claim missing work is complete. |

Partial boundary years must be disclosed when comparing annual totals. Avoid
claims that housing causes crashes; no population or traffic exposure adjustment
is included. If housing means new construction only, review source program/type
fields first: affordable housing production can include preservation.

## A practical Git workflow

Git shares versions of files. The shared data contract and website interfaces are
what make those files work together.

1. Before starting: `git switch main` then `git pull --ff-only` (save your own work first).
2. Create one task branch: `git switch -c member2/rq3-rq4`.
3. Keep the shared names in the team brief. Each website function accepts the
   filtered integrated dataframe and returns a Plotly figure. RQ1–RQ2 belong to
   Member 1, RQ3–RQ4 to Member 2, through RQ11–RQ12 for Member 6.
4. Run `python -m unittest discover -s tests -v` from the repository root.
5. Commit only your intended files, push the branch, and open a pull request to
   main. Include what changed, how it was checked, and a screenshot or notebook link.
6. One teammate reviews and merges. Everyone pulls main again before their next task.

Avoid having several people regenerate `df_integrated.csv` independently. Member 3
owns that output and documents schema changes before merging them. Avoid editing
the same notebook simultaneously; integrate reviewed sections in a final notebook
near submission. A successful merge still needs application tests.

## Run and deploy

Local dashboard: install `requirements.txt`, then `python app/app.py` from the root.
Tests: `python -m unittest discover -s tests -v`.
Render build: `pip install -r requirements.txt`.
Render start: `gunicorn --chdir app app:server --bind 0.0.0.0:$PORT`.
Keep `df_integrated.csv` in the deployed checkout. Test search, filters, empty
results and Generate Report on the deployed site before recording its URL.
No deployment or GitHub push was performed by this review.

## Verified repair checks

- Seven regression tests cover real-data keys, exact integration reproduction,
  search, empty results, report HTTP callbacks, chart values and all 16 category
  combinations for RQ1–RQ8.
- Integration reproduces 484 matched rows from 1,155 housing and 829 transportation
  ZIP-year groups; 671 housing-only and 345 transport-only groups are excluded.
- The 29 unknown source housing-unit values are skipped by aggregation, not
  established as zero. Observed totals may undercount. Six borough disagreements
  are resolved by the existing housing-majority convention; this is documented,
  not presented as externally verified ZIP geography.

## What to ask teammates for

1. Person 2: original transportation cleaning/EDA notebook, raw download or exact
   download parameters and date, and reasons for null/outlier/duplicate handling.
   The supplied cleaned crash snapshot ends June 30, 2026; confirm extraction scope.
2. Persons 1–3: confirm the preservation + new-construction scope and treatment of
   missing housing-unit values. Do not label all production as newly built housing.
3. Persons 5–6: finish RQ9–RQ12, the story, map, final notebook assembly, real member
   names/IDs and contribution record, and deployed-site verification.
4. All members: supply actual AI prompts used, as requested by the assignment.
   The repair used the user's request to fix persons 1–4 and their six-person
   breakdown; add earlier prompts from each contributor without inventing history.

Notebook validation: `python scripts/check_notebooks.py` passed all four offline
notebooks in fresh kernels (8 + 3 + 9 + 10 code cells). The live-source housing
cleaning notebook was not rerun; its final local-download portability issue was
fixed. Source refresh may change the snapshot and should be reviewed separately.
