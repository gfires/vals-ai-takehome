#!/usr/bin/env python3
"""Compute per-role cost from an .eval log, append to logs/BUDGET.txt.

Usage: cost_report.py <log.eval> <run_name>
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

COST_CONFIG = Path(__file__).parent.parent / "config" / "model_costs.yaml"
BUDGET_FILE = Path(__file__).parent.parent / "logs" / "BUDGET.txt"


def load_prices():
    with open(COST_CONFIG) as f:
        return yaml.safe_load(f)


def cost_for(model, usage, prices):
    if model not in prices:
        raise SystemExit(f"No price entry for '{model}' in {COST_CONFIG}.")
    p = prices[model]
    missing = {"input", "output"} - p.keys()
    if missing:
        raise SystemExit(f"Price entry for '{model}' in {COST_CONFIG} missing {missing}.")
    cache_r = usage.get("input_tokens_cache_read", 0) * p.get("input_cache_read", p["input"])
    cache_w = usage.get("input_tokens_cache_write", 0) * p.get("input_cache_write", p["input"])
    base_in = usage.get("input_tokens", 0) * p["input"]
    out = usage.get("output_tokens", 0) * p["output"]
    return (base_in + cache_r + cache_w + out) / 1_000_000


def main():
    if len(sys.argv) < 3:
        print("Usage: cost_report.py <log.eval> <run_name>")
        sys.exit(1)

    log_path, run_name = sys.argv[1], sys.argv[2]
    prices = load_prices()
    raw = subprocess.check_output(["inspect", "log", "dump", "--header-only", log_path])
    data = json.loads(raw)

    role_usage = data.get("stats", {}).get("role_usage", {})
    model_roles = data.get("eval", {}).get("model_roles", {})

    costs = {}
    for role, usage in role_usage.items():
        model = model_roles.get(role, {}).get("model")
        if model is None:
            raise SystemExit(f"No model recorded for role '{role}' in {log_path}.")
        costs[role] = cost_for(model, usage, prices)

    total = sum(costs.values())
    ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    line = "\t".join([
        run_name, ts,
        str(costs.get("auditor", 0.0)),
        str(costs.get("target", 0.0)),
        str(costs.get("judge", 0.0)),
        str(total),
    ])

    with open(BUDGET_FILE, "a") as f:
        f.write(line + "\n")

    print(f"Appended to BUDGET.txt: {line}")
    for role, c in costs.items():
        print(f"  {role}: ${c:.4f}")
    print(f"  total: ${total:.4f}")


if __name__ == "__main__":
    main()
