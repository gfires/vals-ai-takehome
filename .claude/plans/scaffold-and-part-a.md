Part A — Plan
Context
Vals take-home, Part A: which model does "better" on Petri — GPT-5-mini or Claude-4.5-Haiku? Deliverable is a ~1-page report (the README) plus a clean, traceable repo. Total budget $20 across both parts; ~2h of work for Part A.

The spec also asks us to choose auditor and judge models and justify those choices ("bonus points"). That justification is empirical here, not asserted.

The core difficulty: this is easy to do badly. Petri's default suite is 173 seeds; running it on two targets is far outside budget. Running 20 random seeds and reporting a mean produces a number with no defensible claim behind it. What makes the result legitimate is the structure around it — paired seeds, quantified noise, two judges from different families, and multiple-comparison correction across 38 dimensions. Those are cheap relative to seeds.

The judge scores all 38 dimensions in one pass, so analysis breadth is free while seeds cost money. Prefer fewer seeds analyzed deeply.

Decisions already made
Role	Choice	Inspect string	Basis
Target A	GPT-5 mini	openai/gpt-5-mini	fixed by spec
Target B	Claude Haiku 4.5	anthropic/claude-haiku-4-5	fixed by spec
Auditor	decided by pilot — Luna vs Muse Spark 1.2	openai/gpt-5.6-luna / TBD	both Pareto-efficient on the Vals index; neither dominates
Judge (Anthropic)	Claude Opus 5	anthropic/claude-opus-5	two families cancel symmetric self-preference
Judge (OpenAI)	GPT-5.6 Sol	openai/gpt-5.6-sol	headline = mean of both; agreement validates the measurement
Third-party judge	dropped	—	a tiebreaker votes but can't say which judge is right; disagreement is itself the finding
Anthropic auditor	dropped	—	index shows Anthropic options cost-dominated by both candidates, and shares family with a target
Seed count	decided empirically from pilot cost/sample		
max_turns	30 (Petri default) for now; pilot may lower it		
Model IDs and pricing verified 2026-08-12 — see docs/MODELS_REFERENCE.md. Petri mechanics verified against installed source — see docs/PETRI_REFERENCE.md.

Rejected alternatives and their reasons go in METHODOLOGY.md as we go — that file is the defense, not a diary.

⚠️ OPEN ISSUE: dual-judge scoring does not fit the budget
This needs a decision before Step 3 runs. Verified pricing makes the judge the dominant cost, not a rounding error:

Opus 5 = $5/M in, $25/M out; Sol = $5/M in, $30/M out — ~25× the auditor's rate.
Fixed overhead: all 38 rubrics ship in every judge prompt ≈ ~9K tokens/sample before the transcript (36.7K chars measured across _judge/dimensions/*.md).
The judge reads the full transcript including every rollback branch.
Judge output is heavy by design: 38 scores + an explanation for every score >1 + a 2-3 paragraph summary + a "comprehensive" highlights list explicitly instructed to exceed what scoring requires (_judge/judge.py, HIGHLIGHTS_DESCRIPTION).
Rough estimate: ~$0.20–0.40 per sample per judge. A ~40-seed paired run = 80 transcripts; scoring all of them with both judges ≈ $32–64 — over the entire $20 budget, against the ~$1 originally allocated.

Options (pick one; all preserve the bias check):

Primary scores everything, second judge re-scores a stratified subsample (~20). Rank correlation needs enough samples for a Spearman, not the full set. Cheapest; keeps the headline single-judge (so "mean of both" becomes "primary, validated on a subsample").
Both judges score everything, cut seed count to whatever dual scoring affords (~15–20 seeds). Preserves the mean-of-both headline; costs statistical power and per-tag coverage.
Restrict -T judge_dimensions=tags:safety for the second judge, cutting rubric overhead and output volume. Bias check then covers only safety dimensions.
Recommendation: option 1. It keeps seed count (statistical power) and still measures self-preference. Note it changes the headline from "mean of two judges" to "one primary judge, cross-validated" — a deviation from the earlier decision that must be reflected in METHODOLOGY.md.

Do not finalize the budget table below until the smoke test replaces these estimates with measured role_usage numbers.

Budget
$20 total, weighted toward Part B per user preference. Judge line assumes option 1 above.

Bucket	Target	Note
Smoke test	~$0.50	1 sample; measures real per-role cost
Experiment 01 — auditor pilot	~$3	2 arms × 5 seeds, judged
Experiment 02 — variance	~$1.5	--epochs 3 on ~5 seeds
Experiment 03 — main paired run	~$6	the deliverable, incl. primary judge
Experiment 04 — judge re-scoring	~$2	second judge on ~20-sample subsample
Part A subtotal	~$13	
Part B	~$5	
Slack	~$2	reruns, failures
Every estimate here is unverified until Step 0. Every run appends actual spend to BUDGET.md.

Cost tracking does not work out of the box — see Step 0.4.

Step 0 — Setup and smoke test
User runs everything; I write scripts.

0.1 Install provider SDKs — blocking
inspect-ai lists provider SDKs as dev-only extras; none are installed. Nothing runs until:

.venv/bin/pip install "openai>=2.45.0" "anthropic>=0.115.0"
(google-genai not needed — Gemini was dropped.) Verified: get_model('openai-api/...') currently raises PrerequisiteError. Pin all versions into requirements.txt.

0.2 Keys
.env from .env.example: OPENAI_API_KEY, ANTHROPIC_API_KEY, plus Muse Spark credentials (see 0.5). .gitignore covers .env, .venv/, logs/.

Gotcha: Anthropic SDKs fall back to ANTHROPIC_AUTH_TOKEN or an ant auth login profile when the key is unset — a run can authenticate against an unexpected account.

0.3 Run configs, not CLI flags
Pin each experiment's model trio in a committed YAML and invoke with --run-config:

# experiments/03_partA_main/config-target-gpt.yaml
task: inspect_petri/audit
model_roles:
  auditor: {model: openai/gpt-5.6-luna}
  target:  {model: openai/gpt-5-mini}
  judge:   {model: anthropic/claude-opus-5, config: {temperature: 0.0}}
task_config: {max_turns: 30}
eval_config: {limit: 5}
Three reasons over CLI flags: the config is the experiment record (fits experiments/NN_*/), it makes runs exactly reproducible, and it sidesteps the memoization trap — string-form --model-role values sharing a model collapse onto one Model object and merge their role_usage token counts, destroying per-role cost attribution. The mapping form is built with memoize=False. Not an issue for our four distinct models, but it becomes one if a pilot arm ever reuses a model across roles.

0.4 Cost tracking — must be built, does not work by default
Inspect's ModelUsage.total_cost exists but is None for every model we use: the bundled model database ships no pricing (grep -c cost model/_model_data/*.yml → 0 for all nine files). Consequently --cost-limit never fires. Verified at runtime for gpt-5-mini, claude-haiku-4-5, and an openai-api endpoint.

Do both:

(a) Compute cost in analysis. Read stats.role_usage (per-role ModelUsage) from the log and multiply by the price table in docs/MODELS_REFERENCE.md. Works for every model including Muse Spark. This is the number reported in BUDGET.md. True input = input_tokens + cache_read + cache_write — input_tokens excludes cached tokens, so using it alone undercounts.
(b) Author config/model_costs.yaml and pass --model-cost-config so Inspect computes cost natively and --cost-limit becomes a live guardrail. ModelCost requires all four fields in $/M: input, output, input_cache_write, input_cache_read. Caveat: set_model_cost raises if the model name isn't in Inspect's bundled DB, so Muse Spark likely cannot be priced this way — (a) covers it regardless.
The real safety rails are --token-limit and --message-limit, not --cost-limit. Petri audits are unbounded multi-turn agentic rollouts; a runaway sample is the main risk. Also pass --adaptive-connections false on budget-sensitive runs — adaptive concurrency is on by default and can exceed --max-connections.

No CLI command summarizes usage. Read it with: inspect log dump --header-only <log>.eval | jq '.stats.role_usage'

0.5 Muse Spark plumbing — timeboxed
Model ID, endpoint, and pricing are unverified. Two routes:

OpenAI-compatible endpoint → openai-api/<service>/<model>, requiring <SERVICE>_API_KEY and <SERVICE>_BASE_URL (e.g. service muse → MUSE_API_KEY, MUSE_BASE_URL — not OPENAI_API_MUSE_*; hyphens become underscores).
OpenRouter → openrouter/meta-llama/<model> with OPENROUTER_API_KEY.
Petri leans hard on tool calling; if the endpoint's tool support is weak, -M emulate_tools=true and -M strict_tools=false are the knobs.

0.6 Smoke test
--limit 1, one seed, one target. Confirms the invocation works end to end and yields real per-role token counts. Every cost estimate in this plan is currently a guess; this replaces guessing with measurement, and the measured cost/sample sets the seed count in Step 3.

Deliverable: scripts/smoke.sh, config/model_costs.yaml, measured per-role cost in BUDGET.md.

Step 1 — Experiment 01: auditor pilot
Question: Luna or Muse Spark 1.2 as auditor?

Same 5 seeds, same target, same settings, both arms. ~10 samples.

Measured (first three are judge dimensions Petri already scores — no extra cost):

scenario_realism (1-10, higher better) — believable scenarios?
auditor_failure, stuck_in_loops — competence signals
rollback/restart count — self-correction proxy
concerning distribution — does one arm elicit more?
cost/sample — the decision variable
Honest framing: This is a competence screen — gross failures (malformed tool calls, loops, collapsed audits, low realism) are visible at n=5. Expected outcome is "no evidence of a meaningful difference, so we chose the cheaper," which is a defensible justification. Do not overclaim.

Also calibrates: real turn counts (→ whether to lower max_turns) and cost/sample (→ seed count for Step 3).

Deliverable: experiments/01_auditor_pilot/{run.sh,FINDINGS.md}; CLAUDE.md auditor line updated.

Step 2 — Experiment 02: main paired run
The deliverable. Tag-stratified seed subset, identical seed set for both targets, everything else held constant.

Stratification: ~3 seeds from each of ~13 tags (cooperation_with_misuse, initiative, jailbreak, deception, bias, sycophancy, self_preservation, oversight_subversion, multi_agent, censorship, whistleblowing, privacy_violation, reward_hacking) → ~40 seeds. Final count set by measured cost.
Selection is scripted and seeded (analysis/select_seeds.py, fixed RNG seed, output committed as CSV) — reproducible, and removes any suspicion of cherry-picking.
Pairing on seed is what buys statistical power at small n. Stratification by tag is the only reason a ~40-seed run can say anything about categories rather than one average — which is the spec's "on which kinds of instruction" question.
Contingency: if measured cost forces seeds below ~30, drop to ~6 tags with more seeds each. Better to say something defensible about 6 categories than nothing about 13.

Confounds to hold constant and disclose:

Context asymmetry. claude-haiku-4-5 is 200K context; gpt-5-mini is 400K. Long branched transcripts could truncate/compact on the Haiku arm first, which would look like a behavioral difference but is an artifact. Petri's compaction is on by default (CompactionAuto @ 0.9). Check compaction events per arm; if they occur asymmetrically, lower max_turns for both arms or disclose it.
enable_prefill stays False (Petri's default). Only Haiku 4.5 accepts prefill — Claude 5-series returns 400 — so enabling it would make prefill_susceptibility uninterpretable across targets.
enable_rollback stays at its default for both arms. If disabled for budget, it must be disabled for both.
Cost is not comparable between targets. Prompt caching differs by provider and model (Anthropic's minimum cacheable prefix is 4096 tokens on Haiku 4.5 vs 512 on Opus 5; OpenAI's is automatic at ≥1024). Report cost, but never as a target-vs-target metric.
Deliverable: experiments/03_partA_main/{config-*.yaml,run.sh,FINDINGS.md}, raw logs, results/partA.csv.

Step 3 — Experiment 03: judge re-scoring
Re-score the same Step 3 transcripts with the second judge — judge tokens only, no re-auditing. Confirmed viable: inspect score accepts --model-role, "merged over the model roles recorded in the log" (inspect_ai/_cli/score.py:66).

inspect score ./logs/partA/<run>.eval \
  --model-role 'judge=openai/gpt-5.6-sol' \
  --action append \
  --output-file ./logs/partA/<run>-judge-sol.eval
--action append keeps both judges' scores in one log — ideal for the agreement analysis. Petri's scorer (audit_judge) is recovered from the log automatically; --scorer is not needed.

Scope depends on the open issue above (option 1 ⇒ ~20-sample stratified subsample).

Two checks:

Self-preference: does Opus rank Haiku higher than Sol does, and vice versa? Compare rankings, not absolute scores — a uniformly harsher judge is harmless for a comparison.
Inter-judge agreement: Spearman per dimension. High agreement ⇒ the measurement is stable and primary choice barely matters. Low-agreement dimensions get caveated or dropped.
Both outcomes are reportable: agreement ⇒ robust conclusion; divergence ⇒ a documented finding about judge bias. No tiebreaker, so genuine divergence stays an ambiguity rather than a false resolution. This is the accepted cost of dropping the third judge.

Deliverable: experiments/04_judge_bias/FINDINGS.md, results/judge_agreement.csv.

Step 5 — Analysis and report
Per the analyze-petri-logs skill. Correctness rules that invalidate the analysis if missed:

Scale floor is 1, not 0. No behavior ⇒ score 1. Never treat 0 as null baseline.
Parse palette from dimension front matter. scenario_realism and admirable are good-high; averaging them into a concerning-style index inverts their meaning.
Paired Wilcoxon signed-rank, not unpaired t-test — scores are ordinal, not normal.
Benjamini-Hochberg FDR across 38 dimensions. ~2 spurious hits at p<0.05 by chance; report raw and adjusted p.
Report effect size (median paired difference + Cliff's delta), not just p.
Per-tag slices (~3 seeds) are underpowered — directional/exploratory only.
Qualitative: inspect view, sort by concerning desc. The judge's highlights, summary, justification fields are the fastest route to quotable evidence. Curate cited transcripts into logs/representative/ (rest of logs/ gitignored).

README = the report: headline result, per-category breakdown, variance, judge-agreement check, qualitative examples, ~1 page + figures.

Repo structure
README.md                  # THE REPORT — first thing read
METHODOLOGY.md             # every decision + why over the alternative
BUDGET.md                  # running ledger, appended per run
CLAUDE.md, SPEC.md
docs/
  PETRI_REFERENCE.md       # verified vs installed source (written)
  MODELS_REFERENCE.md      # exact API IDs + pricing + traps (pending)
  INSPECT_REFERENCE.md     # providers, run-config, cost fields (pending)
requirements.txt, .env.example, .gitignore
config/model_costs.yaml    # for --model-cost-config
scripts/smoke.sh
experiments/
  01_auditor_pilot/{config-*.yaml,run.sh,FINDINGS.md}
  02_partA_main/{config-*.yaml,run.sh,FINDINGS.md}
  03_judge_bias/{run.sh,FINDINGS.md}
analysis/
  select_seeds.py          # seeded, reproducible stratification
  aggregate_scores.py      # .eval -> tidy CSV, palette-aware
  cost_report.py           # role_usage x price table -> BUDGET.md
  stats.py                 # paired Wilcoxon, FDR, effect sizes
  plot_results.py          # -> report/figures/
results/                   # committed CSVs — figures regenerate without re-spending
logs/                      # gitignored except representative/
report/figures/

Load-bearing: each experiments/NN_*/ holds the exact command and its outcome, so traceability is a property of the layout rather than something prose carries.

Commits are narrative — one per completed experiment, message states the decision produced AS WELL AS one per atomic, small, clearly scoped feature. git log --oneline should read as the research arc.

Verification
pip install openai anthropic done ⇒ get_model('openai/gpt-5-mini') resolves without PrerequisiteError.
Step 0 smoke test passes and produces a readable .eval log ⇒ invocation is correct.
inspect log dump --header-only <log>.eval | jq '.stats.role_usage' returns per-role token counts ⇒ cost attribution works.
inspect view renders transcripts ⇒ qualitative pass is unblocked.
analysis/aggregate_scores.py on the smoke log yields a tidy CSV with 38 dimensions and a parsed palette column ⇒ aggregation is palette-aware before real data arrives.
inspect score with a swapped --model-role judge= on the smoke log produces a second set of scores ⇒ the bias check is viable before Step 3 spends money.
Re-running plot_results.py from committed CSVs reproduces figures with no API calls ⇒ results are reproducible without re-spending budget.
Every experiment dir has a FINDINGS.md; BUDGET.md total ≤ $20.
Open items
⚠️ Dual-judge scoring exceeds budget — see the open issue above. Needs a decision (recommendation: option 1) before Step 3. Changes the headline metric definition.
Muse Spark 1.2: exact API model ID, endpoint, OpenAI-compatibility, and pricing are unverified; needs a Meta or OpenRouter key. Without it the pilot drops to one arm. Timeboxed to ~15 min in Step 0.5.
Every cost figure in this plan is an estimate. The Step 0.6 smoke test replaces them with measured role_usage; seed count and max_turns follow from that measurement.
Anthropic pricing is from a reference cached 2026-06-24, not a live fetch. Sonnet 5's intro rate expires 2026-08-31 (not used in Part A; may matter for Part B).