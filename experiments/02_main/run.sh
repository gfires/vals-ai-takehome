#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

log_dir=logs/02_main

run_eval() {
  local config="$1" label="$2"
  echo "=== $label ==="
  if ! inspect eval inspect_petri/audit \
    --run-config "experiments/02_main/$config" \
    --log-dir "$log_dir" \
    --adaptive-connections false; then
    echo "WARN: $label failed — continuing" >&2
    return 1
  fi
}

process_logs() {
  echo "=== Processing logs ==="
  for log in "$log_dir"/*.eval; do
    json="${log%.eval}.json"
    [ -f "$json" ] && continue
    inspect log dump --resolve-attachments full "$log" > "$json"
    python3 analysis/cost_report.py "$log" "02_main"
    python3 scripts/summarize_run.py "$json"
  done
}

# Phase 1: Luna judge (primary) — GPT-5-mini got 9 original seeds, then 3 supplement
run_eval config-gpt5mini-luna-9.yaml          "GPT-5-mini + Luna (9 seeds)"
run_eval config-gpt5mini-luna-supplement.yaml  "GPT-5-mini + Luna (3 supplement seeds)"

# Phase 1: Luna judge (primary) — Haiku full 12
run_eval config-haiku-luna-full.yaml           "Haiku + Luna (12 seeds)"

# Phase 2: Sonnet judge (self-preference probe) — 4 seeds each
run_eval config-haiku-sonnet.yaml              "Haiku + Sonnet (4 seeds)"
run_eval config-gpt5mini-sonnet.yaml           "GPT-5-mini + Sonnet (4 seeds)"

process_logs
echo "=== DONE ==="
