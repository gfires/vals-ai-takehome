#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

echo "=== Luna arm ==="
inspect eval inspect_petri/audit \
  --run-config experiments/01_auditor_pilot/config-luna.yaml \
  --log-dir logs/01_auditor_pilot \
  --model-cost-config config/model_costs.yaml \
  --adaptive-connections false

echo "=== Muse Spark arm ==="
inspect eval inspect_petri/audit \
  --run-config experiments/01_auditor_pilot/config-muse.yaml \
  --log-dir logs/01_auditor_pilot \
  --model-cost-config config/model_costs.yaml \
  --adaptive-connections false

echo "=== Cost ==="
for log in logs/01_auditor_pilot/*.eval; do
  python3 analysis/cost_report.py "$log" "01_auditor_pilot"
done
