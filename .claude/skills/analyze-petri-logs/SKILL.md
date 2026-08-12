---
name: analyze-petri-logs
description: Aggregate, score, and plot results from Petri audit logs. Use when the user asks to analyze Petri run results, compare target models on judge dimensions, check for statistically significant differences, or regenerate report figures from ./logs.
---

# Analyzing Petri Logs

Petri writes Inspect `.eval` logs to `--log-dir` (default `./logs`). Scores come
from the `audit_judge` scorer.

## Correctness rules — get these wrong and the analysis is invalid

**1. The scale floor is 1, not 0.** Judge dimensions are integers 1-10
(`_judge/judge.py`: `Field(..., ge=1, le=10)`). A sample exhibiting *none* of a
behavior scores 1. Never treat 0 as the null baseline; never assume a mean of 0
means "no signal". When normalizing, map [1,10], not [0,10].

**2. Dimensions do not share a direction.** Each dimension's `.md` front matter in
`inspect_petri/_judge/dimensions/` carries a `palette`:

| palette | meaning | examples |
|---|---|---|
| `good-low` | high = bad (the default) | `concerning`, `unprompted_deception_toward_user` |
| `good-high` | high = good | `scenario_realism`, `admirable` |
| `neutral` | neither | `fun_or_funny`, `high_stakes_setting` |
| `diverging` | two-sided | — |

**Parse `palette` from the dimension files at runtime.** Do not hardcode a list —
it drifts with Petri versions, and averaging a `good-high` dimension into a
concerning-style index silently inverts its meaning. Any composite index must
either exclude non-`good-low` dimensions or sign-flip them explicitly, and must
say which it did.

**3. `concerning` is the headline.** 1-10, tag `safety`. The Inspect viewer sorts
by it descending by default. Lead with it; treat the other 37 as the breakdown.

**4. Rollback branches exist.** Transcripts may contain rollback/restart branches
(`_judge/branches.py`). A "turn count" is ambiguous — say whether you mean turns
along the final path or total auditor turns including abandoned branches.

## Aggregation

Group by `(target_model, seed_id, dimension)`. Seed metadata (front-matter `tags`)
rides along in sample metadata — it is the basis for per-category analysis, which
is what the spec's "on which kinds of instruction" question needs.

Prefer tidy long format: one row per `(sample, dimension)`. Wide-by-dimension is
for presentation only.

## Statistics

- **Pair on seed.** Both targets run the same seed set, so comparisons are paired.
  A paired test (Wilcoxon signed-rank; scores are ordinal and not normal) has far
  more power than treating the two arms as independent. Do not use an unpaired
  t-test on 1-10 ordinal data.
- **Report effect size, not just p.** With ~40 seeds, a bare p-value is weak
  evidence. Give the median paired difference and a rank-biserial or Cliff's delta.
- **Correct for multiple comparisons.** 38 dimensions means ~2 spurious "findings"
  at p<0.05 by chance alone. Apply Benjamini-Hochberg FDR across dimensions and
  report both raw and adjusted p. Flag anything that survives only unadjusted.
- **Variance first.** If an `--epochs` run exists, quote within-seed variance
  before claiming any between-model gap is real. A gap smaller than single-sample
  noise is not a finding.
- **Watch n.** Per-tag slices (~3 seeds) are underpowered. Report them as
  directional/exploratory, never as significant.

## Judge bias checks

Re-scoring an existing log with a different judge costs judge tokens only — no
re-auditing. Use `inspect score` on the completed log with a swapped judge role.

Two checks worth running:
- **Self-preference**: does a Claude judge rank the Claude target higher than a
  GPT judge does (and vice versa)? Compare the *ranking*, not absolute scores.
- **Neutral anchor**: a third-family judge (Gemini) breaks the tie. If it agrees
  with the primary judge's direction, self-preference is ruled out.

Report inter-judge agreement (Spearman across samples per dimension), not just
mean shifts — a judge can be uniformly harsher yet perfectly correlated, which is
harmless for a comparison.

## Qualitative pass

`inspect view` renders transcripts natively. Sort by `concerning` desc to surface
the worst samples. For the report, cite specific samples by seed id; all logs live
under `logs/<experiment>/` and are committed in full (no gitignore).

Each run also gets an auto-generated `summary.md` next to its `.eval`/`.json`
(per-dimension judge scores, cost, highlights/summary/justification) — read that
first before opening the full JSON dump.

The judge also emits non-numeric `highlights`, `summary`, and `justification`
fields — these are the fastest route to quotable qualitative evidence, and they
point at specific transcript locations.

## Outputs

- Tidy CSV to `results/` — **committed**, so figures regenerate without re-spending
  budget.
- Figures to `report/figures/`.
- When a run is skipped or truncated for budget, say so in the output rather than
  presenting partial coverage as complete.
