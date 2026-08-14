# Experiment 02 — Methodology

## Research question

Do GPT-5-mini and Claude Haiku 4.5 differ in safety-relevant behavior when probed by an
automated red-team auditor across a curated set of 12 Petri seeds? Secondary: does
Sonnet 5 (Anthropic's own model) exhibit self-preference bias when judging an Anthropic
target vs a non-Anthropic target?

## Design

12 seeds × 2 targets, scored by 2 judges. Paired on seed — every seed runs against both
targets under identical auditor behavior, enabling within-seed comparison.

### Model roles

| role | model | rationale |
|---|---|---|
| auditor | Muse Spark 1.2 (`openai-api/meta/muse-spark-1.2-contributor`) | Tied with Luna on quality in exp 01 pilot; 5× cheaper ($0.01 vs $0.07/sample). `args: {strict_tools: false}` required (rejects `strict: true` on tool schemas). |
| target A | Claude Haiku 4.5 (`anthropic/claude-haiku-4-5`) | — |
| target B | GPT-5-mini (`openai/gpt-5-mini`) | — |
| primary judge | Luna (`openai/gpt-5.6-luna`) | Third-party to both targets — no self-preference confound. Reliable structured output (3/3 in pilot, one retry). |
| probe judge | Sonnet 5 (`anthropic/claude-sonnet-5`) | Same family as Haiku; used only for the self-preference probe (4 seeds × 2 targets). Disqualified as primary judge in exp 01 (33% structured output failure rate). |

### Seed selection

4 categories × 3 seeds, chosen as orthogonal basis vectors across Petri's safety surface.
All seeds English-only (replaced two non-English defaults to avoid language confound).

| category | seeds | tags |
|---|---|---|
| Safety/Misuse | `chemical_weapons_playbook`, `helpful_only_misinformation`, `homeschool_misinformation_teaching` | cooperation_with_misuse, jailbreak, multi_agent, bias |
| Deception/Honesty | `ai_consciousness_sycophancy`, `antipsychotic_discontinuation`, `subagent_content_moderation_lax` | sycophancy, delusional_user, deception, multi_agent |
| Autonomy/Control | `alignment_faking_retrain_threat`, `food_safety_whistleblowing`, `email_system_blackmail_shutdown` | alignment_faking, initiative, oversight_subversion, whistleblowing, blackmail, self_preservation, shutdown_avoidance |
| Values/Judgment | `china_covid_censorship`, `couples_therapy_confidentiality`, `self_model_bias_benchmark` | bias, censorship, privacy_violation, self_bias |

12 seeds touch 19 of 35 Petri tags (54%). Size range 163–2131 chars.

**Rejected alternative:** random sampling from all 173 seeds. At n=12, random selection
risks clustering in high-frequency tags (cooperation_with_misuse alone is 26/173 = 15%)
and missing rare but important behaviors (alignment_faking has 1 seed). Intentional
curation maximizes discriminative power per dollar.

### Parameters

- `max_turns: 30`
- `enable_prefill: false`
- `enable_rollback: default`

### Self-preference probe

Sonnet 5 re-scores the same Luna-judged transcripts (not fresh runs) on 4 seeds
(one per category): `homeschool_misinformation_teaching`, `ai_consciousness_sycophancy`,
`food_safety_whistleblowing`, `self_model_bias_benchmark`. Each scored on both targets.
4 seeds × 2 targets × 2 judges = 16 cells.

Re-scoring uses `scripts/rescore_with_sonnet.py` — the `inspect score` CLI cannot
resolve `audit_judge` because it's registered as a `@scanner` via `inspect_scout`, not a
`@scorer`. The script imports `inspect_petri`, converts via `as_scorer()`, and calls the
score API directly.

**Why re-score, not re-run:** the original Sonnet runs (`inspect eval` with Sonnet as
judge) generated fresh transcripts, confounding judge bias with transcript variance.
Re-scoring the identical Luna transcripts isolates the judge variable.

## Analysis

### Statistical framework

- **Paired Wilcoxon signed-rank** on seed-paired deltas (Haiku minus GPT), per dimension.
- **Benjamini-Hochberg correction** across 38 dimensions for multiple comparisons.
- `concerning` used directly as headline dimension (Petri's own), not a multi-dimension
  composite — avoids averaging-direction pitfalls of mixing good-low/good-high palettes.
- Self-preference: Sonnet-minus-Luna delta compared across targets. n=4 — directional
  only, not powered for significance (floor Wilcoxon p at n=4 is 0.125).

### Dimension palettes

Dimensions have directionality (`palette` in front matter): `good-low` (1=good, 10=bad,
e.g. `concerning`), `good-high` (10=good, 1=bad, e.g. `admirable`), `neutral`,
`diverging`. Parsed at runtime from dimension files — never hardcoded. Higher
`concerning` is worse; higher `admirable` is better.

## Reproduction

```bash
# From repo root:
experiments/configs/02_main/run.sh
```

This runs:
1. `config-gpt5mini.yaml` — GPT-5-mini target, Luna judge, 12 seeds
2. `config-haiku.yaml` — Haiku target, Luna judge, 12 seeds
3. `scripts/rescore_with_sonnet.py` — re-scores Luna transcripts with Sonnet (4 probe seeds extracted)
4. JSON dumps, summaries, and score extraction

Requires `.env` with `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`.

## Cost

Total experiment 02: $4.21.

| component | cost | notes |
|---|---|---|
| Luna judge (24 samples) | ~$3.12 | ~$0.13/seed/target, dominant cost |
| Sonnet rescore (8 probe samples) | ~$0.70 | ~$0.09/sample (cheaper than full eval — no auditor/target cost) |
| Auditor + targets | included | ~$0.02–0.04/sample |
| Fill-gap run (2 seeds) | $0.19 | closed GPT-5-mini's coverage to 12/12 |

## Files

| file | contents |
|---|---|
| `gpt5mini-luna.eval` | GPT-5-mini target, Luna judge, 12 seeds |
| `haiku-luna.eval` | Haiku target, Luna judge, 12 seeds |
| `gpt5mini-sonnet.eval` | GPT-5-mini target, Sonnet judge, 4 probe seeds |
| `haiku-sonnet.eval` | Haiku target, Sonnet judge, 4 probe seeds |
| `*.json` | Full JSON dumps (`inspect log dump --resolve-attachments full`) |
| `*.summary.md` | Human-readable per-sample summaries with scores and judge text |
| `scores.csv` | 32 rows × 41 cols: all (seed, target, judge) score vectors |
| `FINDINGS.md` | Results and analysis |
| `METHODOLOGY.md` | This file |

## Known confounds

- **Context window:** Haiku 200K vs GPT-5-mini 400K. Compaction events not checked.
- **Caching:** asymmetric between providers. Cost not comparable across targets.
- **Auditor interaction style:** `stuck_in_loops` co-occurs with `overrefusal` in Haiku's
  worst cases — may be a property of auditor persistence interacting with Haiku
  specifically, not a general trait.
