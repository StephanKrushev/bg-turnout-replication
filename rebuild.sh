#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export MPLBACKEND=Agg
python reproduce.py > results.txt
for script in age_backcast forecast_figure generational_turnout_figure publication_benchmark ou_sensitivity paper_figures; do
    python "$script.py"
done
for pass in 1 2; do
    pdflatex -halt-on-error -interaction=nonstopmode working_paper.tex > /dev/null
done
