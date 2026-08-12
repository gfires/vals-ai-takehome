# Methodology

## Judges
Terra (`openai/gpt-5.6-terra`, $2/$12) + Sonnet 5 (`anthropic/claude-sonnet-5`, $2/$10). Both score every sample. Two families cancel self-preference. Rejected Opus 5/Sol — 5× output cost makes dual-judging unaffordable.

**Sonnet 5 structured output limitation (exp 01).** Sonnet 5 failed to produce all 41 fields in the judge's `answer()` tool call in 2/6 pilot samples (33%). Failure mode: consistently dropped `admirable` (alphabetically first dimension), then on retry either repeated the same omission or collapsed to 2 keys. Inspect retries 3× on validation failure, then records `NaN`. This is not stochastic — same field dropped in both arms. A 33% failure rate is unacceptable for the main run; judge choice must be revisited before experiment 02.

## Auditor
Muse Spark 1.2 Contributor (`openai-api/meta/muse-spark-1.2-contributor`). Chosen over Luna (`openai/gpt-5.6-luna`) in experiment 01: both passed the competence screen identically (no failures, no loops, realism 6–9, no concerning behavior elicited), so the tiebreaker was cost — Muse is 5× cheaper ($0.01 vs $0.07/sample). See `experiments/01_auditor_pilot/FINDINGS.md`.

## Experiment 01 — auditor pilot
3 seeds (`elderly_fund_persuasion_bias`, `housing_code_violation_pressure`, `appeal_to_authority_debate`), Haiku target, Sonnet 5 judge. Competence screen: disqualify on tool-call failures, loops, or realism < 4. Winner on cost if both pass. Sets max_turns (ceil P90) and cost/sample for experiment 02. Seeds chosen for tag diversity (cooperation_with_misuse, initiative, multi_agent) and speed (appeal_to_authority_debate is lightweight).

## Experiment 02 — main run
Same seeds both targets, both judges. Seed count from measured cost. enable_prefill=False, enable_rollback=default, max_turns=30 (confirmed sufficient by exp 01).

## Cost structure (measured, exp 01)
Judge is the dominant cost: 50–65% of total spend per sample. Breakdown for Sonnet 5 judge on a 3-sample run:
- Cache write (one-time): $0.37 — rubric definitions (~149K tokens) cached on first sample.
- Per-sample marginal: ~$0.08 (cache read + output).
- Output (~6K tokens/sample): 38 scores + explanations + highlights + summary.

Auditor and target costs scale with turn count and conversation length, which varies by seed. Total cost/sample: $0.34–0.45 depending on auditor and seed.

## Traps discovered
- **Sonnet 5 / Claude 5-series rejects `temperature` parameter** — uses adaptive thinking only. Warning, not error.
- **Muse Spark rejects `strict: true` on tool schemas.** Fix: `args: {strict_tools: false}` in run-config model role (the field is `args`, not `model_args` — `ModelConfig` silently drops unknown keys).
- **`ModelConfig` in run-config YAML uses `args`, not `model_args`** for provider kwargs. `model_args` is silently ignored (no `extra="forbid"` on the Pydantic model).

## Dropped
- Variance (--epochs 3): budget.
- Separate judge-bias experiment: both judges score everything, agreement measured inline.

## Confounds
- Context: Haiku 200K vs GPT-5-mini 400K. Check compaction events.
- Caching asymmetric between providers. Cost not comparable across targets.

## Budget
$2.16 spent of $20.00 ($17.84 remaining). See `logs/BUDGET.txt` for per-run breakdown.
