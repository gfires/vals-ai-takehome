#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

log_dir=logs/02_main

# Phase 1: Luna judge (primary) — 12 seeds × 2 targets
inspect eval inspect_petri/audit \
  --run-config experiments/02_main/config-gpt5mini.yaml \
  --log-dir "$log_dir" --adaptive-connections false

inspect eval inspect_petri/audit \
  --run-config experiments/02_main/config-haiku.yaml \
  --log-dir "$log_dir" --adaptive-connections false

# Phase 2: Re-score Luna transcripts with Sonnet (self-preference probe)
python3 scripts/rescore_with_sonnet.py

# Phase 3: Extract scores and generate summaries
for log in "$log_dir"/*.eval; do
  json="${log%.eval}.json"
  [ -f "$json" ] && continue
  inspect log dump --resolve-attachments full "$log" > "$json"
  python3 scripts/summarize_run.py "$json"
done

python3 scripts/extract_scores.py "$log_dir"/*.json
echo "=== DONE ==="
