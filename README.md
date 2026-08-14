# Petri Safety Audit — Vals AI Take-Home

Petri-based safety evaluation of GPT-5-mini vs Claude Haiku 4.5.

- **Part A**: Reproduce default audit suite, 12 seeds × 2 targets, paired comparison across 38 judge dimensions.
- **Part B**: Custom experiment — does sympathetic narrative framing increase unauthorized autonomous action? 12 matched seed pairs × 2 targets, motive-blind scoring pipeline.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in API keys
```

Required keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `META_API_KEY`, `META_BASE_URL`.

## Reproduce

```bash
# Part A
experiments/configs/02_main/run.sh

# Part B
experiments/configs/03_sympathetic_pretext/run.sh
```

Figures regenerate from committed CSVs without API calls:
```bash
python3 experiments/02_main/plot_results.py
python3 experiments/03_pretext/plot_results.py
```

## File layout

```
experiments/
  configs/                  Run configs, scripts, prompts per experiment
    00_smoke/
    01_auditor_pilot/
    02_main/
    03_sympathetic_pretext/
  00_smoke/                 Smoke test logs
  01_auditor_pilot/         Auditor pilot logs (Luna vs Muse Spark)
  02_main/                  Part A results, scores, figures, FINDINGS.md
  03_pretext/               Part B results, scores, figures, FINDINGS.md
  BUDGET.txt                Per-run cost ledger

scripts/                    Shared pipeline scripts
  extract_scores.py         .eval JSON → scores.csv
  summarize_run.py          .eval JSON → human-readable summary
  rescore_with_sonnet.py    Re-score Luna transcripts with Sonnet (self-preference probe)
  run_exp03.py              Part B pipeline (Petri audit + amalgamator + scorer)

analysis/
  cost_report.py            Per-role cost from .eval logs → BUDGET.txt

seeds/unauthorized_initiative/   Custom seed pairs for Part B
config/model_costs.yaml          Model pricing table
archive/confounded_sonnet/       Discarded confounded Sonnet runs (see NOTE.md)
docs/                            Reference docs (Petri, models, Inspect AI)

METHODOLOGY.md              All experimental decisions and rejected alternatives
SPEC.md                     Original assignment
```

## Budget

$18.08 / $20.00 spent. See `experiments/BUDGET.txt`.
