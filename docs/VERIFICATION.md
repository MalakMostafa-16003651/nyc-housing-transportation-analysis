# Verification results

Audit completed November 7–8, 2026 (Africa/Cairo), using Python 3.12.14 and the
versions in `requirements-analysis.txt`. The operating system was Windows.

| Check | Observed result |
| --- | --- |
| Supplied CSV comparison | All three attachments match repository records and values. |
| Raw provenance | Both official archived raw CSV SHA-256 checks pass. |
| Cleaning | Every supplied source field reproduced from the archived raw snapshots. |
| Integration | Exact reproduction of all 484 committed integrated rows; one row per ZIP/year; no output nulls or duplicate keys. |
| Regression suite | **25 tests passed**, including seven cleaning, seven integration and eleven dashboard tests. |
| Fresh notebook kernels | **7 notebooks passed; 73 code cells; zero error outputs**. |
| Saved artifacts | Executed notebooks refreshed; four PNG figures regenerated and visually reviewed. |
| Browser HTTP and JavaScript | Local dashboard returns HTTP 200; no uncaught page errors observed. |
| Browser report interaction | Search by borough/year, both measure dropdowns, Generate Report, unsupported-ZIP rejection and single-ZIP selection passed. |
| Browser charts | Twelve numbered figure containers render; RQ1–RQ12 are implemented (RQ11–RQ12 added November 8). Separate selected-measures explorer updates both axes. |
| Mobile layout | 390-pixel viewport has 390-pixel document width; no horizontal overflow. |
| Map and trend visual review | Real basemap and data markers render; annual trend spacing reviewed and corrected. |
| Whitespace check | `git diff --check` passes. |
| Production deployment | `render.yaml` added; gunicorn start command verified locally (HTTP 200). Live URL: see README once deployed and tested. |

Fresh notebook code-cell counts: housing cleaning 27, transportation cleaning 5,
integration 9, Person 1 research 8, Person 2 research 3, Person 4 research 10,
Person 5 research 11. A final label-only refresh reran Persons 1 and 4 research
and visually checked their four static figures.

Browser numeric checks observed the initial 112,688 affordable units and 5,881
serious crashes across 143 ZIPs. Searching Brooklyn/2023–2025/severe gave 27,859
affordable units and 1,921 severe injuries across 37 ZIPs. Changing both dropdowns
and generating a report gave 741 summed housing-building counts and 137 fatalities
for that selection. The unsupported ZIP search retained that report.

Notebook checks and the browser used local processes outside the restrictive
network sandbox to allow Jupyter kernels and the browser/server to communicate.
An initial sandbox-only attempt and an initial test fixture using the restricted
OS temporary directory were corrected before the successful runs. A successful
local run does not verify a production deployment.

The checks support correctness of the recorded transformations and tested
interactions. They do not remove the source geography omissions, unknown unit
counts, borough conventions or selection bias documented in `PROJECT_REVIEW.md`.

## Person 6 checks (November 8, 2026, Linux, Python 3.12)

| Check | Observed result |
| --- | --- |
| Regression suite | **29 tests passed** (25 existing + 4 for RQ11/RQ12). |
| Fresh notebook kernels | `scripts/check_notebooks.py`: **8 notebooks passed**, including `Person6_Research_Questions.ipynb` (13 code cells). Its final cell confirms the website's RQ11/RQ12 functions reproduce the notebook values. |
| Production server | `gunicorn --chdir app app:server` (Render's start command) serves HTTP 200 and the Dash layout. |
| Browser end-to-end (headless Chrome against gunicorn) | 12 chart cards, no chart errors. Initial summary 112,688 units / 5,881 crashes / 143 ZIPs. Search `Bronx 2023 2025 severe` → 27,160 units, 1,200 severe injuries, 22 ZIPs; RQ11 regrouped (8/3/3/8) and RQ12 showed only the Bronx (ρ = 0.57, n = 22). Transportation dropdown → Fatalities + Generate Report → 393 fatalities; RQ11/RQ12 axes switched to fatalities. Unknown ZIP `99999` rejected with a warning. |
| Map basemap | Not verifiable in the sandbox (the basemap host is blocked there); must be checked on the live URL. |
