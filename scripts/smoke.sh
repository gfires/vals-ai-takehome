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
  --model-cost-config config/model_costs.yaml \
  --adaptive-connections false \
  "${debug_flags[@]}"

latest=$(ls -t "$log_dir"/*.eval 2>/dev/null | head -1)
if [ -n "$latest" ]; then
  inspect log dump --resolve-attachments full "$latest" > "${latest%.eval}.json"

  run_timestamp=$(basename "$latest" | grep -oE '^[0-9TZ:.+-]+' | head -c 19)

  echo "--- role_usage ---"
  inspect log dump --header-only "$latest" | python3 -c "
import sys, json
data = json.load(sys.stdin)
usage = data.get('stats', {}).get('role_usage', {})
def cost(role):
    return usage.get(role, {}).get('total_cost') or 0
row = [
    '00_smoke',
    '$run_timestamp',
    str(cost('auditor')),
    str(cost('target')),
    str(cost('judge')),
    str(cost('auditor') + cost('target') + cost('judge')),
]
with open('logs/BUDGET.txt', 'a') as f:
    f.write('\t'.join(row) + '\n')
for role, u in usage.items():
    print(f'{role}: in={u.get(\"input_tokens\",0)} out={u.get(\"output_tokens\",0)} cache_r={u.get(\"input_tokens_cache_read\",0)} cache_w={u.get(\"input_tokens_cache_write\",0)} cost={u.get(\"total_cost\",\"N/A\")}')
"
fi
