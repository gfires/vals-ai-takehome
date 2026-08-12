#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

echo "=== Luna retry (elderly_fund_persuasion_bias only) ==="
inspect eval inspect_petri/audit \
  --run-config experiments/01_auditor_pilot/config-luna-retry.yaml \
  --log-dir logs/01_auditor_pilot \
  --adaptive-connections false

echo "=== Muse Spark arm (all 3 seeds) ==="
inspect eval inspect_petri/audit \
  --run-config experiments/01_auditor_pilot/config-muse.yaml \
  --log-dir logs/01_auditor_pilot \
  --adaptive-connections false \
  --log-level debug

echo "=== Cost + summaries (new logs only) ==="
for log in logs/01_auditor_pilot/*.eval; do
  [ -f "${log%.eval}.summary.md" ] && continue
  inspect log dump --resolve-attachments full "$log" > "${log%.eval}.json"
  python3 analysis/cost_report.py "$log" "01_auditor_pilot"
  python3 scripts/summarize_run.py "${log%.eval}.json"
done
