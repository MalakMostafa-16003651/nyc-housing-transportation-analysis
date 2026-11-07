# Data provenance and audit outputs

The authoritative integrated file is `df_integrated.csv` at the repository root.
The website checks that file first and validates its schema, keys and measures.
Missing or invalid data produces an explicit error; no random results are substituted.

## Raw sources

`raw/` contains official NYC Open Data snapshots recovered during the November 7,
2026 audit, their source metadata and a manifest with retrieval URLs, dimensions
and SHA-256 checksums. These are archived inputs for offline cleaning, not a claim
that every source record has usable geography. The recovered snapshots reproduce
the supplied cleaned datasets. Reconstructed cleaning documents the reproducible
method; it does not prove who performed the original work.

- Housing: [Affordable Housing Production by Building](https://data.cityofnewyork.us/d/hg8x-zxpr), ID `hg8x-zxpr`.
- Transportation: [SIRTA](https://data.cityofnewyork.us/d/xeqp-qz8h), ID `xeqp-qz8h`.

Run the two cleaning notebooks or use `scripts/cleaning.py`. Read their EDA and
exclusion counts before changing the cleaning policy. Future API results may
include revisions; changing the raw snapshots requires deliberate review and
regeneration of the downstream data, charts and findings.

## Integration evidence

- `integration_audit.json`: source quality, aggregation and matching summaries.
- `unmatched_zip_years.csv`: all 1,016 housing-only or transportation-only groups.
- `borough_disagreements.csv`: six matched groups with differing source boroughs.
- Root `df_housing_agg.csv`, `df_transport_agg.csv`: separately aggregated inputs.

Run `python scripts/integration.py` to verify the integrated snapshot, or add
`--write` to intentionally regenerate outputs. See [the integration method](../docs/INTEGRATION_METHOD.md).

## Map positions

`zip_centroids.csv` retains its historical filename, but its latitude/longitude
values are means of available source housing/crash coordinates within each ZIP.
They are approximate marker locations, not official ZIP centroids or polygon
boundaries. `Person5_Research_Questions.ipynb` rebuilds them. The map reports missing
coordinates rather than silently inventing locations. Map tiles require internet
access; the CSV data and statistical charts run locally.
