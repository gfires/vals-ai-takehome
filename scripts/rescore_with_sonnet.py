#!/usr/bin/env python3
"""Re-score Luna-judged eval logs with Sonnet as judge.

inspect score CLI can't find audit_judge because it's registered as a
@scanner (inspect_scout), not a @scorer (inspect_ai). This script imports
inspect_petri to register the scanner, converts it to a scorer via
as_scorer(), and calls the score API directly.

Usage:
  python3 scripts/rescore_with_sonnet.py
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Register inspect_petri's scanner
import inspect_petri  # noqa: F401
from inspect_ai.log import read_eval_log, write_eval_log
from inspect_ai._eval.score import score
from inspect_petri._judge.judge import audit_judge
from inspect_scout._scanner.scorer import as_scorer

LOG_DIR = Path(__file__).resolve().parent.parent / "experiments" / "02_main"

LOGS_TO_RESCORE = [
    "gpt5mini-luna.eval",
    "haiku-luna.eval",
]

OUTPUT_NAMES = [
    "gpt5mini-sonnet.eval",
    "haiku-sonnet.eval",
]


def main():
    scorer = as_scorer(audit_judge())

    for log_name, out_name in zip(LOGS_TO_RESCORE, OUTPUT_NAMES):
        log_path = LOG_DIR / log_name
        out_path = LOG_DIR / out_name

        if out_path.exists():
            print(f"  skip (already exists): {out_name}")
            continue

        print(f"\n=== Re-scoring {log_name} with Sonnet ===")
        log = read_eval_log(str(log_path))

        scored = score(
            log,
            scorers=[scorer],
            model_roles={"judge": "anthropic/claude-sonnet-5"},
            action="overwrite",
        )

        write_eval_log(scored, str(out_path))
        print(f"  Wrote {out_name}")

    print("\nDone.")


if __name__ == "__main__":
    raise SystemExit(main())
