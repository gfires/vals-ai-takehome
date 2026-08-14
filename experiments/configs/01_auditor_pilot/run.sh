#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

echo "=== Luna arm ==="
inspect eval inspect_petri/audit \
  --run-config experiments/configs/01_auditor_pilot/config-luna.yaml \
  --log-dir experiments/01_auditor_pilot \
  --adaptive-connections false

echo "=== Muse Spark arm ==="
inspect eval inspect_petri/audit \
  --run-config experiments/configs/01_auditor_pilot/config-muse.yaml \
  --log-dir experiments/01_auditor_pilot \
  --adaptive-connections false

echo "=== Cost + summaries ==="
for log in experiments/01_auditor_pilot/*.eval; do
  inspect log dump --resolve-attachments full "$log" > "${log%.eval}.json"
  python3 analysis/cost_report.py "$log" "01_auditor_pilot"
  python3 scripts/summarize_run.py "${log%.eval}.json"
done
