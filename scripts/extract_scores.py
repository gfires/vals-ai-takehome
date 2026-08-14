#!/usr/bin/env python3
"""Append rows to experiments/02_main/scores.csv from one or more Petri run JSON dumps.

Usage: extract_scores.py <run.json> [<run.json> ...]
Each <run.json> must be a full `inspect log dump --resolve-attachments full`
output (same input as scripts/summarize_run.py). Skips (seed, target, judge)
rows already present in scores.csv so re-running is idempotent.
"""

import csv
import json
import sys
from pathlib import Path

SCORES_CSV = Path(__file__).resolve().parent.parent / "experiments/02_main/scores.csv"


def rows_from_run(run_json_path):
    d = json.loads(Path(run_json_path).read_text())
    target = d["eval"]["model_roles"]["target"]["model"].split("/")[-1]
    judge = d["eval"]["model_roles"]["judge"]["model"].split("/")[-1]
    reduction = next(r for r in d["reductions"] if r["scorer"] == "audit_judge")
    seed_ids = [s["id"] for s in d["samples"]]
    rows = []
    for seed_id, sample_score in zip(seed_ids, reduction["samples"]):
        row = {"seed": seed_id, "target": target, "judge": judge}
        row.update({k: int(v) for k, v in sample_score["value"].items()})
        rows.append(row)
    return rows


def main(argv):
    if not argv:
        print(__doc__)
        return 1

    existing_rows = []
    fieldnames = None
    if SCORES_CSV.exists():
        with SCORES_CSV.open() as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            existing_rows = list(reader)
    existing_keys = {(r["seed"], r["target"], r["judge"]) for r in existing_rows}

    new_rows = []
    for path in argv:
        for row in rows_from_run(path):
            key = (row["seed"], row["target"], row["judge"])
            if key in existing_keys:
                print(f"skip (already present): {key}")
                continue
            if fieldnames is None:
                fieldnames = list(row.keys())
            new_rows.append(row)
            existing_keys.add(key)

    if not new_rows:
        print("Nothing new to add.")
        return 0

    all_rows = existing_rows + new_rows
    with SCORES_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Added {len(new_rows)} row(s) to {SCORES_CSV}")
    for row in new_rows:
        print(f"  + {row['seed']}, {row['target']}, {row['judge']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
