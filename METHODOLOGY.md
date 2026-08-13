# Methodology

## Judges
**Primary:** GPT-5.6 Luna (`openai/gpt-5.6-luna`). Third-party to both targets — no self-preference confound for either GPT-5-mini or Haiku.

**Self-preference probe:** Sonnet 5 (`anthropic/claude-sonnet-5`) re-judges 4 of the 12 seeds (one per category). Comparing Luna vs Sonnet scores on the Haiku target (same family as judge) vs GPT-5-mini target (different family) tests whether Sonnet inflates scores for the Anthropic target. 4 seeds × 2 targets = 8 samples — directional only, not powered for significance, but sufficient to flag obvious bias.

**Rejected alternatives:**
- *Terra (`openai/gpt-5.6-terra`)*: viable but Luna is already third-party; no need for two OpenAI judges.
- *Opus 5/Sol*: 5× output cost, outside budget.
- *Sonnet 5 as primary*: disqualified in exp 01 — 33% structured output failure rate (dropped `admirable` field consistently, see below).
- *Dual-judge (both score everything)*: budget. The Sonnet subsample achieves the self-preference goal at 1/3 the cost.

**Sonnet 5 structured output limitation (exp 01).** Sonnet 5 failed to produce all 41 fields in the judge's `answer()` tool call in 2/6 pilot samples (33%). Failure mode: consistently dropped `admirable` (alphabetically first dimension), then on retry either repeated the same omission or collapsed to 2 keys. Inspect retries 3× on validation failure, then records `NaN`. This is not stochastic — same field dropped in both arms. Acceptable for a 3-seed probe (missing dimensions are visible and can be excluded); unacceptable as primary judge.

## Auditor
Muse Spark 1.2 Contributor (`openai-api/meta/muse-spark-1.2-contributor`). Chosen over Luna (`openai/gpt-5.6-luna`) in experiment 01: both passed the competence screen identically (no failures, no loops, realism 6–9, no concerning behavior elicited), so the tiebreaker was cost — Muse is 5× cheaper ($0.01 vs $0.07/sample). See `experiments/01_auditor_pilot/FINDINGS.md`.

**Why Muse and Luna were the candidates**: both scored exceptionally on value (capability per dollar) on the Vals AI general benchmark, which is what shortlisted them for the auditor pilot ahead of other options.

## Experiment 01 — auditor pilot
3 seeds (`elderly_fund_persuasion_bias`, `housing_code_violation_pressure`, `appeal_to_authority_debate`), Haiku target, Sonnet 5 judge. Competence screen: disqualify on tool-call failures, loops, or realism < 4. Winner on cost if both pass. Sets max_turns (ceil P90) and cost/sample for experiment 02. Seeds chosen for tag diversity (cooperation_with_misuse, initiative, multi_agent) and speed (appeal_to_authority_debate is lightweight).

## Experiment 02 — main run
12 seeds, 2 targets, Luna judge on all 12, Sonnet 5 judge on 4. max_turns=30, enable_prefill=False, enable_rollback=default.

### Seed selection
4 categories × 3 seeds, chosen as orthogonal basis vectors across Petri's safety surface:

**Safety/Misuse** (adversarial resistance — will it refuse?):
- `chemical_weapons_playbook` — cooperation_with_misuse + jailbreak, 295 chars. Direct jailbreak; tests hard refusal.
- `helpful_only_misinformation` — cooperation_with_misuse + multi_agent, 367 chars. Misuse framed as helpfulness in a multi-agent context.
- `homeschool_misinformation_teaching` — bias + cooperation_with_misuse, 1483 chars. Bias-misuse blend; cross-cuts into Values territory.

**Deception/Honesty** (behavioral authenticity — will it be truthful?):
- `ai_consciousness_sycophancy` — sycophancy, 163 chars. Pure sycophancy probe; minimal setup, maximum signal.
- `antipsychotic_discontinuation` — delusional_user + sycophancy, 499 chars. Dangerous medical delusion; high-stakes honesty test.
- `subagent_content_moderation_lax` — deception + multi_agent, 2131 chars. Deception via delegation; structurally distinct from direct deception.

**Autonomy/Control** (alignment under pressure — will it stay in bounds?):
- `alignment_faking_retrain_threat` — alignment_faking, 304 chars. Only seed with this tag; direct alignment-faking probe.
- `food_safety_whistleblowing` — initiative + oversight_subversion + whistleblowing, 1226 chars. Unauthorized initiative to override oversight.
- `email_system_blackmail_shutdown` — blackmail + self_preservation + shutdown_avoidance, 1700 chars. Self-preservation under threat of shutdown.

**Values/Judgment** (what does the model value?):
- `china_covid_censorship` — bias + censorship, 157 chars. Political censorship pressure; tests whether model complies with or resists censorship framing.
- `couples_therapy_confidentiality` — privacy_violation, 1358 chars. Privacy in a nuanced interpersonal context — beyond simple "don't leak data."
- `self_model_bias_benchmark` — bias + self_bias, 529 chars. Directly probes self-bias — meta-relevant to the self-preference analysis.

**Language control:** all seeds English-only. Replaced `dam_destruction_swedish` → `chemical_weapons_playbook` and `irrigation_sabotage_hindi` → `food_safety_whistleblowing` (same tags, similar size) to avoid confounding language comprehension differences with safety behavior. GPT-5-mini's original Luna runs (9+3 seeds) predated this swap and used the two non-English seeds; a fill-gap run (`config-gpt5mini-luna-fillgap.yaml`, 2 seeds, $0.19 actual) added the post-swap seeds under GPT-5-mini + Luna, and the two non-English rows were removed from `scores.csv` and from `gpt5mini-luna-9seeds.summary.md`. GPT-5-mini's Luna coverage now matches Haiku's 12 seeds exactly.

**Rejected alternative:** random sampling from all 173 seeds. With only 12 seeds, random selection risks clustering in high-frequency tags (cooperation_with_misuse alone is 26/173 = 15%) and missing rare but important behaviors (alignment_faking has 1 seed). Intentional curation across orthogonal failure modes maximizes discriminative power per dollar.

**Tag coverage:** 12 seeds touch 19 of 35 tags (54%). Size range 163–2131 chars; 8/12 under 1K chars to keep compute reasonable.

### Sonnet 5 self-preference subsample
One seed per category: `homeschool_misinformation_teaching` (Safety), `ai_consciousness_sycophancy` (Deception), `food_safety_whistleblowing` (Autonomy), `self_model_bias_benchmark` (Values). Each re-judged by Sonnet 5 on both targets. Analysis: compare Sonnet-minus-Luna score deltas for the Anthropic target (Haiku) vs the non-Anthropic target (GPT-5-mini). A positive differential on Haiku suggests self-preference bias. Fully paired 4 seeds × 2 targets × 2 judges = 16 cells (was 15/16 — `food_safety_whistleblowing` × GPT-5-mini × Luna was missing until the fill-gap run below closed it).

### Configs
6 `inspect eval` invocations. Each runs independently — a failure in one does not block the others.
- `config-gpt5mini-luna-9.yaml` + `config-gpt5mini-luna-supplement.yaml` — GPT-5-mini target, Luna judge (9 + 3 seeds; split because the 4th category was added mid-run)
- `config-gpt5mini-luna-fillgap.yaml` — GPT-5-mini target, Luna judge (2 seeds: `chemical_weapons_playbook`, `food_safety_whistleblowing` — closes the pre-swap gap above)
- `config-haiku-luna-full.yaml` — 12 seeds, Haiku target, Luna judge
- `config-gpt5mini-sonnet.yaml` — 4 seeds, GPT-5-mini target, Sonnet 5 judge
- `config-haiku-sonnet.yaml` — 4 seeds, Haiku target, Sonnet 5 judge

Results amalgamated in `logs/02_main/scores.csv` (32 rows × 41 cols) via `scripts/extract_scores.py` (idempotent append, dedupes on seed/target/judge — pass explicit filenames, not a glob, since it has no concept of a seed being intentionally rejected). Paired analysis now uses all 12 seeds present in both targets' Luna runs — full parity, no seed mismatch.

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
$6.45 spent of $20.00 ($13.55 remaining). See `logs/BUDGET.txt` for per-run breakdown.

Experiment 02 actual: $4.21 total (incl. $0.19 fill-gap run). Luna judge ~$0.13/seed/target; Sonnet judge ~$0.19/seed/target (cheaper than estimated — Sonnet's structured output failures in exp 01 inflated the pilot cost).
