# Findings

Running log of what we found, across both experiments. Source of record for the README;
not all of this will make the one-pager. See METHODOLOGY.md for what we did and why over
the rejected alternative; this file is the results and the interpretation.

## Experiment 01 — Auditor pilot

**Question:** Luna (`openai/gpt-5.6-luna`) or Muse Spark 1.2
(`openai-api/meta/muse-spark-1.2-contributor`) as auditor? Full setup in
`experiments/01_auditor_pilot/FINDINGS.md`.

**Why these two candidates specifically:** both scored exceptionally on value
(capability per dollar) on the Vals AI general benchmark — that's what put them in the
running as auditor candidates over other options, before the pilot ever ran.

**Result:** Both passed the competence screen identically at n=3 seeds — no tool-call
failures, no loops, realism 6–9, neither elicited concerning behavior (expected at this
n). No evidence of a quality difference between them. Muse is ~5x cheaper as auditor
($0.01/sample vs Luna's $0.07/sample).

**Decision:** Muse Spark chosen as auditor. With scores tied, cost broke the tie.

**Judge side-finding:** Sonnet 5 was piloted as judge in the same run and failed 2/6
samples (33%) — it could not reliably produce all 41 fields (38 dimensions +
highlights + summary + justification) in the structured `answer()` tool call.
Deterministic, not stochastic: `admirable` (alphabetically first dimension) was the
consistent drop target across both failures, surviving 3 retries in one case by
collapsing to 2 keys. This disqualified Sonnet 5 as primary judge for experiment 02 —
**Luna was promoted to judge** on the strength of scoring reliably (3/3, one retry) in
the same pilot, alongside its Vals-benchmark value credentials. Sonnet 5 was kept on for
a smaller role instead (self-preference probe, exp 02), where a lower reliability bar
and smaller n were acceptable.

**Net effect on exp 02's model roles:** auditor=Muse (cost), primary judge=Luna
(reliability), Sonnet 5=secondary/probe judge only (already disqualified as primary,
repurposed for the one question where its own family membership matters).

---

## Experiment 02 — Main run (Part A)

Full results, data, and methodology: `logs/02_main/` (FINDINGS.md, METHODOLOGY.md,
scores.csv).
