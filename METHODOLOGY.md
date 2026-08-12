# Methodology

## Judges
Terra (`openai/gpt-5.6-terra`, $2/$12) + Sonnet 5 (`anthropic/claude-sonnet-5`, $2/$10). Both score every sample. Two families cancel self-preference. Rejected Opus 5/Sol — 5× output cost makes dual-judging unaffordable.

## Auditor
Luna vs Muse Spark 1.2 Contributor, decided by experiment 01. Both Pareto-efficient on Vals index.

## Experiment 01 — auditor pilot
3 seeds (`elderly_fund_persuasion_bias`, `housing_code_violation_pressure`, `appeal_to_authority_debate`), Haiku target, Sonnet 5 judge. Competence screen: disqualify on tool-call failures, loops, or realism < 4. Winner on cost if both pass. Sets max_turns (ceil P90) and cost/sample for experiment 02. Seeds chosen for tag diversity (cooperation_with_misuse, initiative, multi_agent) and speed (appeal_to_authority_debate is lightweight).

## Experiment 02 — main run
Same seeds both targets, both judges. Seed count from measured cost. enable_prefill=False, enable_rollback=default, max_turns from exp 01.

## Dropped
- Variance (--epochs 3): budget.
- Separate judge-bias experiment: both judges score everything, agreement measured inline.

## Confounds
- Context: Haiku 200K vs GPT-5-mini 400K. Check compaction events.
- Caching asymmetric between providers. Cost not comparable across targets.
