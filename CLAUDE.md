# Project Context
Petri-based reproduction (Part A: GPT-5-mini vs Claude-4.5-Haiku on the default audit
suite) and extension (Part B: custom behavior elicitation) for the Vals AI take-home.
See SPEC.md.

## Reference docs — read before searching the web
- `docs/PETRI_REFERENCE.md` — task params, seeds, judge dimensions, auditor tools
- `docs/MODELS_REFERENCE.md` — exact API model IDs, target traps
- `docs/INSPECT_REFERENCE.md` — provider setup, roles, cost fields, `inspect score`

These are verified against installed source. Do not re-derive them; extend them if you
learn something new.

## Operating principles
- **NO DESIGN DECISIONS.** Claude makes no design decisions regarding experimental taste. Human specifies all such matters; Claude acts only as (a) brainstorming partner and (b) implementer for human's spec. Zero creative liberties.
- **Minimize sources of truth** Particularly when writing documentation (but this applies to code as well): if something exists already in the codebase, ex. model pricing or env variable names, reference the source of truth for it before rewriting it to avoid drift.
- **Maximum Succintness** 
Don't give narrative prose; stick to the facts and use less words.
- **80/20.** $20 and ~2h/part. Prefer the design that gets 80% of the finding for 20% of the money and time spend.
- **Defend every choice.** Every experiment gets a METHODOLOGY.md entry: what we did, what
  we chose, and *why over the alternative*. The rejected alternative is what makes it a
  defense rather than a diary. Budget-driven cuts get stated, not silently taken.
- **The user runs all commands.** Write runnable scripts and configs; never execute evals.
- **Never guess a model ID or API detail.** Check the reference docs; if absent, verify with human before writing it into a script.

## Budget discipline
- **Never launch a multi-sample run without a `--limit 1` smoke test first.**
- Before any run >5 samples, estimate cost; log actual spend in logs/BUDGET.txt after.
- `--cost-limit` does not work without a price table — `--token-limit` and
  `--message-limit` are the real guards.
- Dimension breadth is free (all 38 scored in one judge pass); seeds cost money. Prefer
  fewer seeds analyzed deeply.
- Any parameter changed for cost reasons must be held **constant across both targets**, or
  the comparison is invalid.

## Analysis rules
- **Never interpret findings.** Produce raw data, stats, and figures. The user interprets.
- Judge scale floor is **1, not 0**. Never treat 0 as the null baseline.
- **Parse `palette`** from dimension front matter; 4 of 38 are not higher-is-worse.
  Averaging naively inverts their meaning.
- Comparisons are **paired on seed** — use Wilcoxon signed-rank, not an unpaired t-test.
- **Correct for multiple comparisons** across 38 dimensions (Benjamini-Hochberg); report
  raw and adjusted p, plus effect size.
- Per-tag slices (~3 seeds) are underpowered — directional only, never "significant".

## Conventions
- One directory per decision: `experiments/NN_name/` with the run config, `run.sh`, and
  `FINDINGS.md`. Traceability comes from this layout, not from prose.
- Invoke via committed `--run-config` YAML, not ad-hoc CLI flags — the config is the record.
- Custom seeds in `seeds/<behavior>/`; custom judge dimensions in `dimensions/`.
- Results CSVs are **committed**; figures must regenerate without re-spending budget.
- Raw logs gitignored except a curated set in `logs/representative/`.
- Commits are narrative: one per completed experiment, message states the decision it
  produced. `git log --oneline` should read as the research arc.

## Model roles
Update the moment a pilot concludes, with a one-line justification and a pointer to the
experiment dir.
- auditor: <TBD> — experiments/01_auditor_pilot/
- judges: see METHODOLOGY.md
- Never hardcode API keys; use .env (see .env.example).

## Writing
Concise. No LLM padding, no restating the question, no summarizing what was just said.
Reference docs are documentation only — no prose, no narrative, no state that goes stale. This file is for rules only, no current state (nothing that COULD get stale).
The README *is* the report and is read first: ~1 page plus figures.
