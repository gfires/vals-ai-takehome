#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

inspect eval inspect_petri/audit \
  --run-config experiments/00_smoke/config.yaml \
  --log-dir logs/smoke \
  --model-cost-config config/model_costs.yaml \
  --adaptive-connections false

echo "--- role_usage ---"
latest=$(ls -t logs/smoke/*.eval 2>/dev/null | head -1)
if [ -n "$latest" ]; then
  inspect log dump --header-only "$latest" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for role, usage in data.get('stats', {}).get('role_usage', {}).items():
    print(f'{role}: in={usage.get(\"input_tokens\",0)} out={usage.get(\"output_tokens\",0)} cache_r={usage.get(\"input_tokens_cache_read\",0)} cache_w={usage.get(\"input_tokens_cache_write\",0)} cost={usage.get(\"total_cost\",\"N/A\")}')
"
fi
