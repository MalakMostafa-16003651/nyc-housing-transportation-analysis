# Archived source snapshots

These files were retrieved from NYC Open Data on **2026-11-07** for this audit.
They reproduce every field of the supplied cleaned snapshots after documented
date, ZIP, borough and year transformations. This is evidence of reproducibility,
not proof of the original extraction date or individual authorship.

| Archived dataframe | Source | Rows | Columns |
| --- | --- | ---: | ---: |
| `df_housing_raw.csv` | [Affordable Housing Production by Building, hg8x-zxpr](https://data.cityofnewyork.us/d/hg8x-zxpr) | 9,551 | 41 |
| `df_transport_raw.csv` | [SIRTA, xeqp-qz8h](https://data.cityofnewyork.us/d/xeqp-qz8h) | 13,754 | 23 |

`manifest.json` records retrieval date, exact URLs, sizes in rows/columns and
SHA-256 hashes. The adjacent metadata JSON files preserve source field descriptions.
The notebook checker verifies the CSV hashes before running either pipeline.

SIRTA contains crashes analyzed and reported through that program. The recovered
cleaning recipe excludes 5,682 rows without ZIPs, leaving 8,072 retained crashes.
The raw source starts in January 2022; the retained subset starts in October 2022
because earlier records lack ZIPs. The late retained start must not be described
as SIRTA's program start. Calendar-year comparisons still omit unknown-ZIP crashes.
The 44 source ZIP `10000` records are retained and flagged for geographic review;
none matches a housing ZIP-year in the saved integration.

Housing includes preservation and new construction, dated by project start.
Unknown unit counts and unknown ZIPs are retained in its cleaned source table.

Run both cleaning notebooks or `python scripts/check_notebooks.py` from the
repository root. A live refresh is a separate data change: archive a new source,
review quality and selection, then regenerate all downstream datasets and charts
together. Do not silently replace these source files or their hashes.
