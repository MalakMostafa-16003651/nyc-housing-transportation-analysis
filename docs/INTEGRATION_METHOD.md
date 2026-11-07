# Malak's integration: method and interpretation

The shared contract is one row per `zip_code` + `year`. Both sources are aggregated
**before** merging; raw building rows and raw crash rows are never joined. This
prevents multiplying affordable units or injury counts through many-to-many matches.

`scripts/integration.py` owns the reproducible transformation used by
`dataEngP3.ipynb`. The input files are the team's supplied cleaned snapshots, which
are semantically identical to the three CSV attachments supplied for this audit.
The integration does not claim those inputs contain all NYC activity.

| Step | Result on the supplied snapshots |
| --- | --- |
| Housing key check | 9,551 rows; exclude 1,958 with missing ZIP (20.5% of rows, 1.044% of observed affordable units). |
| Transportation key check | 8,072 rows, present ZIP/year, unique crash IDs. |
| Housing aggregation | 1,155 ZIP-year groups; distinct building/project IDs and observed sums of units. |
| Transportation aggregation | 829 ZIP-year groups; distinct crash IDs and sums of severe/non-severe injuries and fatalities. |
| Outer coverage audit | 484 matched, 671 housing-only and 345 transportation-only ZIP-year groups. |
| Analytical join | Retain the 484 matches; unmatched counterpart activity is unknown and never imputed as zero. |
| Final validation | 11 columns; unique ZIP-year keys; no nulls or negative count values for these snapshots. |

Input keys must be integral and ZIPs must have five digits. Boroughs must use the
five NYC names. Known counts must be nonnegative integers. Duplicate crash IDs or
missing injury counts stop integration because summing them would distort totals.
Source date-derived years are checked when date fields are present.

Six matched ZIP-years have different source borough summaries. The existing policy
assigns each ZIP its most frequent housing borough across the housing snapshot
(alphabetical tie break). The disagreement table is retained for review. This is an
analytical convention, not a verified ZIP-boundary correction. Source transportation
ZIPs 11237 and 11385 have Brooklyn/Queens labels. The 44 transportation rows labeled
ZIP `10000` are also flagged, preserved in source aggregates, and excluded from the
matched output because no housing group matches them.

There are 29 unknown source affordable-unit values, including three rows in matched
groups. Partial sums are **observed subtotals**, not proof that missing units equal
zero. `sum(min_count=1)` preserves a wholly unknown group's missing value. Housing
includes preservation and new construction; the year is the project start year,
not building completion year. Summing annual building/project counts counts
ZIP-year appearances and need not equal unique entities across the whole period.

The cleaned transportation snapshot has dates from October 1, 2022 through June 30,
2026. Available ZIP geography and matching select which activity is retained; these
are not complete NYC annual totals. Selecting calendar years 2023–2025 avoids the
boundary dates but does not remove selection bias or establish complete coverage.
The recovered raw SIRTA snapshot has 13,754 rows, including 5,682 with missing ZIP.
The cleaning replay removes three exact duplicates (all missing-ZIP rows) and the
remaining 5,679 missing-ZIP records, yielding the supplied 8,072 rows. Raw source
dates start January 1, 2022; the cleaned sample's October start follows geography
selection. The source snapshots and their provenance are archived in `data/raw/`.
Ratios per affordable unit/project are descriptive comparisons, not traffic risk
rates. Housing production is not population, road length or traffic exposure, and
the correlations cannot establish causation.

Run from the repository root:

```bash
python scripts/integration.py          # compare CSV without modifying it
python scripts/integration.py --write  # regenerate snapshots and audit evidence
python -m unittest discover -s tests -v
```

Generated evidence:

- `df_housing_agg.csv` and `df_transport_agg.csv`: pre-merge source aggregates.
- `df_integrated.csv`: matched analytical sample used by all dashboard charts.
- `data/integration_audit.json`: counts, totals, nulls, caveats and portable LF-normalized source SHA-256 digests.
- `data/unmatched_zip_years.csv`: all excluded groups, with source metrics and merge status.
- `data/borough_disagreements.csv`: the six source borough disagreements.
