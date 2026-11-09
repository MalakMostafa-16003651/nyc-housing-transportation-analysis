# Housing Growth and Road Safety in New York City

An exploratory study of affordable housing production and serious road crashes, with reproducible pandas notebooks and an interactive Dash website.

Results describe **matched ZIP-code/year records**, not all NYC housing or all NYC crashes. Housing production includes **new construction and preservation**, assigned to the housing project's **start year**; it is not completed new housing or net growth. SIRTA describes crashes reviewed by that program, rather than every NYC collision.

## Data and method

| Source | Official dataset | Shared dataframe names |
| --- | --- | --- |
| Housing | [Affordable Housing Production by Building](https://data.cityofnewyork.us/d/hg8x-zxpr), `hg8x-zxpr` | `df_housing_raw`, `df_housing_clean` |
| Transportation | [Serious Injury Response, Tracking & Analysis Program (SIRTA)](https://data.cityofnewyork.us/d/xeqp-qz8h), `xeqp-qz8h` | `df_transport_raw`, `df_transport_clean` |
| Integration | Independently aggregated source tables | `df_integrated` |

The three user-supplied CSVs contain the same records and values as the repository versions. Official raw snapshots were recovered during the November 7, 2026 audit, allowing offline source cleaning. See [data provenance](data/README.md) for URLs, checksums and retrieval details. Future live downloads may contain revisions and should be reviewed before replacing these snapshots.

- Housing: 9,551 raw rows/41 columns; 9,551 cleaned rows/42 columns. Standardize dates, ZIPs, boroughs and project-start year. Retain missing ZIPs and unknown units; retain large valid buildings.
- Transportation: 13,754 raw rows; 8,072 retained rows with a source ZIP. **5,682 rows without ZIPs are excluded**, creating geographic selection bias. October 2022 is the earliest retained ZIP-coded record, not the beginning of the raw source. The reconstructed cleaning notebook reproduces the supplied file; it does not establish original authorship.
- **Aggregate BOTH tables by `zip_code` + `year` before merging.** Count distinct buildings, projects and crash IDs within each group; sum the relevant units and injury/death counts. Never merge raw rows directly.
- Audit an outer join, then use a validated **one-to-one inner join**. Of 1,155 housing and 829 transportation groups, 484 match. The 671 housing-only and 345 transport-only groups are reported, not assumed to be zeros.
- `df_integrated.csv`: **484 rows, 143 ZIPs, 2022–2026**, no duplicate ZIP/year keys or null output cells. Six matched borough disagreements use the documented housing-majority convention, not independently verified ZIP boundaries.
- The 29 unknown source affordable-unit values are skipped by the observed sum, not established as zero. Totals may undercount. Summed annual project/building counts need not be unique projects/buildings over the whole period.

`scripts/integration.py` owns the shared integration logic and audit exports. See [the requirements and verification review](docs/PROJECT_REVIEW.md).

## Team responsibilities

Assignments and names were supplied by the team. File evidence and checks establish deliverables, not individual authorship; audit additions and reconstructed work are identified in the review.

| Person | Member | Responsibility | Two research visualizations |
| --- | --- | --- | --- |
| 1 | Kareem | Housing loading, EDA and cleaning | RQ1: units vs serious crashes by ZIP (scatter). RQ2: housing and crashes by borough (grouped bar). |
| 2 | Youssef | Transportation loading, EDA and cleaning | RQ3: housing and crashes over time (line). RQ4: projects vs severe injuries (scatter). |
| 3 | **Malak** | **ZIP/year aggregation, integration, validation and post-merge cleaning** | RQ5: ZIPs high in housing and crashes (scatter). RQ6: top 10 crash-to-affordable-unit ratios (bar). |
| 4 | Ahmed | Website, filters, search and Generate Report | RQ7: buildings vs severe injuries (scatter). RQ8: crashes per project by borough (bar). |
| 5 | Kenzy | Chart consistency, map and story | RQ9: high-housing/high-crash overlap (map). RQ10: annual housing vs severe injuries (line/scatter analysis). |
| 6 | Lama | Final documentation, testing and deployment | RQ11: ZIPs with high housing but poor road safety (categorized scatter). RQ12: does the housing–crash link differ by borough (borough-coloured scatter + correlation chart). README, testing (notebook checks, unit tests, browser end-to-end checks) and PythonAnywhere deployment (optional Render Blueprint included). |

## Findings and limitations

Within the matched sample, ZIPs with more affordable units tend to have more serious crashes; ZIPs with more housing buildings tend to have more severe injuries. These are descriptive associations. Population, traffic exposure, road length, housing mix and reporting coverage are not controlled for.

Brooklyn leads matched-sample affordable-unit and crash totals. Staten Island has the highest crash-to-project ratio with a small housing denominator. This ratio is **not a population-adjusted safety rate**. RQ6 excludes zero-unit denominators rather than inventing a ratio.

RQ9 defines high as at or above the 75th percentile among ZIPs in the current selection. The full sample has 23 ZIPs high on both. Thresholds change with filters. Marker positions average available housing/crash coordinates; they are **not official ZIP centroids or boundaries**.

RQ11 and RQ12 compare ZIPs **per matched year** (sum ÷ number of matched years), because ZIPs are matched in 1–5 years and summed totals mostly track that coverage (Spearman ρ 0.76 for units and 0.80 for crashes against matched years). RQ11 splits ZIPs at the median of the current selection: 45 of 143 are above median on both affordable units and serious crashes, versus about 25% expected if unrelated. Brooklyn (18) and the Bronx (14) contribute most; 27 high-housing ZIPs have below-median crashes. RQ12 finds a modest citywide per-year association (ρ = 0.30). Only the Bronx shows a clear one (ρ = 0.56, 95% bootstrap interval 0.11–0.86); Brooklyn, Manhattan and Queens are weak (ρ 0.12–0.20, intervals include zero), and Staten Island (7 ZIPs) is too small to judge. A balanced 2023–2025 panel (72 ZIPs) gives the same pattern. These are associations between counts, not risk rates or causal effects.

RQ10 compares ZIPs present in every selected year within 2023–2025. Among those 72 ZIPs, affordable units fell 15.4% (25,494 to 21,562) while severe injuries rose 23.4% (1,177 to 1,453). A balanced panel reduces changing-sample bias but does not restore missing-ZIP records or establish causality. Three interior years cannot establish a general annual relationship. Boundary years and varying ZIP availability require care in time comparisons. Historical p-values are descriptive and do not account for spatial or repeated-observation dependence.

## Run the website

Python 3.12 was used for verification. From the repository root:

```bash
python -m venv .venv
```

Activate with `.\.venv\Scripts\Activate.ps1` in Windows PowerShell or `source .venv/bin/activate` on macOS/Linux, then:

```bash
python -m pip install -r requirements.txt
python app/app.py
```

Open [the local dashboard](http://127.0.0.1:8050). Keep `df_integrated.csv` in the repository root. Missing/invalid data produces an explicit error instead of synthetic results.

Choose boroughs, ZIPs, years and housing/transport measures, then click **Generate Report**. Search examples: `Brooklyn 2023 2025 severe`, `11212 fatalities`. Summary totals and the selected-measures explorer follow both measure selectors. Research charts preserve the measures named in their questions; RQ8 also supports the selected transport measure with a matching title, and RQ11/RQ12 follow both selected measures. Geography/year filters apply throughout, with messages when a chart needs more data. RQ10 uses 2023–2025 only. Generate Report refreshes the on-screen report; it does not download a PDF.

## Analysis and verification

```bash
python -m pip install -r requirements-analysis.txt
python -m unittest discover -s tests -v
python scripts/integration.py
python scripts/check_notebooks.py
```

Notebook checks run in isolated temporary copies with fresh kernels, preserving checked-in CSVs and plots. Cleaning uses archived raw snapshots. To intentionally regenerate integration outputs after reviewing source changes:

```bash
python scripts/integration.py --write
```

Read notebooks in this order:

1. `Housing_Data_Cleaning.ipynb` — housing raw data, EDA and cleaning.
2. `Transport_Data_Cleaning.ipynb` — recovered transportation source, EDA, exclusions and reproducible cleaning.
3. `dataEngP3.ipynb` — Malak's integration and RQ5–RQ6.
4. `Person1_Research_Questions.ipynb`, `Person2_Research_Questions.ipynb`, `RQ7_RQ8_Research_Questions.ipynb`, `Person5_Research_Questions.ipynb`, `Person6_Research_Questions.ipynb` — RQ1–RQ4 and RQ7–RQ12.

Website: `app/app.py`, `app/data_loader.py`, `app/charts/`, `app/assets/style.css`. Automated checks: `tests/`. [AI_PROMPTS.md](docs/AI_PROMPTS.md) preserves the existing prompt record and identifies audit assistance.

## Deployment

**Live website:** [NYC Housing & Road Safety](https://nychousingsafety.pythonanywhere.com/)

**Status: deployed on PythonAnywhere and live browser checks passed on November 8, 2026.** Verified HTTP 200, all twelve research charts, map basemap/markers, borough/year and ZIP searches, both measure selectors, Generate Report, invalid-ZIP feedback, and mobile layout after charts resize. No uncaught JavaScript errors were observed. Initial totals match the reviewed integrated dataset: 112,688 affordable units, 5,881 serious crashes and 143 ZIPs. See [verification evidence](docs/VERIFICATION.md).

### How the live site was deployed (PythonAnywhere)

We used a free PythonAnywhere Beginner account (no payment card needed, and the site does not sleep). Render was tried first, but its free plan asked for a payment card.

1. In a PythonAnywhere **Bash console**:
   ```bash
   git clone https://github.com/MalakMostafa-16003651/nyc-housing-transportation-analysis.git
   mkvirtualenv nycenv --python=python3.12
   pip install --no-cache-dir -r nyc-housing-transportation-analysis/requirements.txt
   ```
2. **Web tab → Add a new web app → Manual configuration → Python 3.12**, then set **Virtualenv** to `nycenv`.
3. Replace the WSGI configuration file with:
   ```python
   import sys
   sys.path.insert(0, "/home/nychousingsafety/nyc-housing-transportation-analysis/app")
   from app import server as application
   ```
4. Click **Reload** on the Web tab.

**Updating the live site:** after changes are pushed to GitHub, run `cd nyc-housing-transportation-analysis && git pull` in a Bash console, then click **Reload**.

`df_integrated.csv` and `data/zip_centroids.csv` are committed, so the app needs no live data download. For local development, run `python app/app.py`.

### Alternative: Render

`render.yaml` is included as an optional second hosting route; it is not the current deployment. On Render, create a web service from this repository with build command `pip install -r requirements.txt` and start command `gunicorn --chdir app app:server --bind 0.0.0.0:$PORT --workers 2 --timeout 120` (Python 3.12.8). Render's free plan may require a payment card.

**Deployment checks** (repeat on the live URL before submission): the page loads with all 12 numbered charts; the map shows a basemap; searching `Bronx 2023 2025 severe` updates the filters and summary; changing the transportation dropdown to *Fatalities* and clicking **Generate Report** updates the summary and charts; searching an unknown ZIP (`99999`) shows a warning without changing the report.

## Submission package and final status

The November 9 final recheck passed **29 regression tests** and **all eight notebooks (86 code cells)**, including Lama's RQ11/RQ12. See [the submission checklist](docs/SUBMISSION_CHECKLIST.md) for requirement-by-requirement evidence and exactly what to submit.

Submit the GitHub repository link, all eight analysis notebooks (or the single combined notebook if your course explicitly requires one), source/cleaned/aggregated/integrated CSVs with provenance, website source and requirements, this README with team contributions, and the **working public website URL above**. The code/data and live deployment requirements in the supplied six-person brief have now been checked. Additional report, slide, video or upload-format requirements must be checked against the course's official submission rubric, which was not supplied here.
