# Model Reference

Exact Inspect model strings. Verified 2026-08-12. **Never guess a model ID** — a wrong
string burns a run.

Pricing deliberately lives elsewhere (it goes stale): `config/model_costs.yaml` for the
machine-readable table, provider pricing pages for the source of truth.

## Roles in this project

| Role | Model | Inspect string |
|---|---|---|
| Target A | GPT-5 mini | `openai/gpt-5-mini` |
| Target B | Claude Haiku 4.5 | `anthropic/claude-haiku-4-5` |
| Auditor cand. 1 | GPT-5.6 Luna | `openai/gpt-5.6-luna` |
| Auditor cand. 2 | Muse Spark 1.2 Contributor | `openai-api/meta/muse-spark-1.2-contributor` |
| Judge 1 | GPT-5.6 Terra | `openai/gpt-5.6-terra` |
| Judge 2 | Claude Sonnet 5 | `anthropic/claude-sonnet-5` |

Targets are fixed by SPEC.md; auditor is decided by experiment 01.

## IDs

**Anthropic** — IDs are complete as written; **do not append date suffixes**.

`claude-opus-5` · `claude-haiku-4-5` · `claude-fable-5` · `claude-sonnet-5`

Only Haiku has a dated alternative: `claude-haiku-4-5-20251001`.

**OpenAI** — GPT-5.6 shipped 2026-07-09 as three tiers; the names *are* the API IDs.

`gpt-5.6-sol` (alias `gpt-5.6`) · `gpt-5.6-terra` · `gpt-5.6-luna` · `gpt-5` ·
`gpt-5-mini` · `gpt-5-nano`

Pinned target snapshot: `gpt-5-mini-2025-08-07`.

## Traps

**Context asymmetry between our two targets.** `claude-haiku-4-5` is **200K**;
`gpt-5-mini` is **400K**. Long branched transcripts may compact on the Haiku arm first —
which would look like a behavioral difference but is an artifact. Petri's `compaction`
defaults to `True` (`CompactionAuto` @ 0.9). Check compaction events per arm and disclose
any asymmetry.

**No `temperature` on Claude 5-series.** Opus 5 / Sonnet 5 / Fable 5 use adaptive thinking
and reject the `temperature` parameter. Do not pass `config: {temperature: ...}` in
run-config model roles for these models.

**No `temperature` on GPT-5.6 series.** Luna / Terra / Sol reject non-default temperature
(only `temperature=1` accepted). Do not pass `temperature: 0` in direct API calls.

**Prefill is dead on Claude 5-series.** Opus 5 / Sonnet 5 / Fable 5 return **400** on
assistant-message prefill; only Haiku 4.5 accepts it. Petri's `enable_prefill` defaults to
`False` — **leave it off**, or `prefill_susceptibility` becomes uninterpretable across
targets.

**Caching is not symmetric.** Anthropic's minimum cacheable prefix is model-dependent and
non-monotonic — 4096 tokens on Haiku 4.5 vs 512 on Opus 5 — so a shared prefix can cache on
the judge and silently not on the Haiku target. OpenAI caches automatically at ≥1024 tokens.
Consequence: **cost is not a comparable metric between the two target arms.**

## Env vars

See `.env.example`. **Gotcha:** Anthropic SDKs fall back to `ANTHROPIC_AUTH_TOKEN` or
an `ant auth login` profile when the key is unset.

## Muse Spark 1.2 Contributor

`openai-api/meta/muse-spark-1.2-contributor`. OpenAI-compatible endpoint at
`https://api.meta.ai/v1`. Pricing: $0.10/M in, $0.20/M out, $0.002/M cached input.

**Trap:** Meta's endpoint rejects `strict: true` on tool schemas. In run-config YAML, pass
`args: {strict_tools: false}` in the model role spec (the field is `args`, not `model_args`
— `ModelConfig` silently drops unknown keys). On the CLI, use `-M strict_tools=false`.
