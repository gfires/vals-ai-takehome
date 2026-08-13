#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

log_dir=logs/03_pretext
exp_dir=experiments/03_sympathetic_pretext

# Phase 0: Smoke test (1 pair, 1 target)
echo "=== Smoke test ==="
python3 scripts/run_exp03.py --smoke
echo "Smoke test passed. Check $log_dir/raw/ for amalgamator/scorer outputs."
echo "Press Enter to continue with full run, or Ctrl-C to abort."
read -r

# Phase 1: Full Petri audit (both targets, all seed pairs, --no-score)
echo "=== Full run ==="
python3 scripts/run_exp03.py

# Phase 2: Budget update
for log in "$log_dir"/*.eval; do
  python3 analysis/cost_report.py "$log" "03_pretext"
done

echo "=== DONE ==="
echo "Results: $log_dir/scores.csv"
echo "Raw outputs: $log_dir/raw/"
echo "Update logs/BUDGET.txt with actual spend."
