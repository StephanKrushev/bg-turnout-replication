# Bulgarian presidential runoff, 2026

Replication materials for Stephan Krushev, *Forecasting Turnout and Reconstructing Participation by Age: Evidence from Bulgaria's Presidential Runoff*, working paper of 8 November 2026. Based on manuscript revision a04ba0f4c5fc1a9f6a45ed35f0ec685769271751. This edition replaces two private repository links with archive file references.

Open working_paper.pdf to read the paper. The results/ folder contains reference outputs. All data used by the build are included. Public source URLs document provenance.

## Reproduce

Tested with Python 3.12.14, Bash and pdfLaTeX. Install a TeX distribution with the packages listed in working_paper.tex (including Latin Modern). From this folder, in a terminal:

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    bash rebuild.sh

The scripts run locally and write regenerated tables, figure files and the paper into this folder. Installation may need network access. The analysis itself runs offline. The fixed random seeds are in the scripts. Floating-point optimizers, linear algebra libraries and PDF metadata can differ across machines.

## Where to look

- Figure 1 uses presidential_history.csv. Each row includes the voter count, denominator and original source.
- Tables 1 and 2 use working_turnout.csv, official_turnout_audit.csv and publication_benchmark.py. The resulting observation_ledger.csv records measurement time, evidence of publication time and coverage limitations. results.txt gives the rolling two-hour forecast errors separately.
- Table 3 and Figure 2 use turnout_filter.py, forecast_figure.py and ou_sensitivity.py. The CSV reports separate intervals for underlying turnout and a future report.
- Table 4 and the two feasibility thresholds use age_backcast.py. It subtracts overseas totals from national totals in vote_counts.csv and applies the nine published within-age choice shares given in the script.
- Figure 3 uses paper_figures.py to construct two illustrative schedules and check their weighted sum at each time. Figure 4 uses the earlier rounded allocation in generational_turnout_figure.py.

## Age data sources

[CIK national count](https://results.cik.bg/pvr202610/tur2/rezultati/index.html) and [overseas count](https://results.cik.bg/pvr202610/tur2/rezultati/32.html) provide votes by choice. [Alpha Research](https://alpharesearch.bg/post/1060-01-noemvri-2026-demografski-profil-na-glasuvalite-na-ii-tur-na-izborite-za-prezident-i-viceprezident.html) provides the conditional choice percentages. The LP measures sensitivity to a uniform tolerance. Its bounds refer to domestic valid votes.
