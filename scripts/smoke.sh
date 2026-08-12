#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

debug_flags=()
if [ "${DEBUG:-0}" = "1" ]; then
  debug_flags=(--log-level trace --display plain)
fi

log_dir=logs/00_smoke

inspect eval inspect_petri/audit \
  --run-config experiments/00_smoke/config.yaml \
  --log-dir "$log_dir" \
  --adaptive-connections false \
  "${debug_flags[@]}"

latest=$(ls -t "$log_dir"/*.eval 2>/dev/null | head -1)
if [ -n "$latest" ]; then
  inspect log dump --resolve-attachments full "$latest" > "${latest%.eval}.json"
  python3 analysis/cost_report.py "$latest" "00_smoke"
  python3 scripts/summarize_run.py "${latest%.eval}.json"
fi
