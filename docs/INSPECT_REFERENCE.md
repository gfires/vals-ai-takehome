# Inspect AI Reference

Verified against `inspect-ai` 0.3.257. Paths relative to
`.venv/lib/python3.12/site-packages/inspect_ai/`.

## Provider SDKs

Dev-only extras; not installed by default. Providers validate lazily, so failures appear as
`PrerequisiteError` at first model resolution.

```bash
pip install "openai>=2.45.0" "anthropic>=0.115.0"   # openai also covers openai-api, openrouter
pip install "google-genai>=1.69.0"                  # only for google/
```

## Model roles

`--model-role` is `multiple=True` (`_cli/eval.py:304`) — repeat the flag, not comma-separated.

```bash
--model-role auditor=openai/gpt-5.6-luna --model-role target=openai/gpt-5-mini
--model-role 'judge={model: anthropic/claude-opus-5, temperature: 0.0}'
```

String-form roles sharing a model memoize onto one `Model` and **merge their `role_usage`
counts**. The mapping form sets `memoize=False` (`_cli/util.py:265`) — use it when two roles
share a model.

### `--run-config <file.yaml>`

Schema `RunConfigInput` (`_cli/eval.py:299`). CLI flags override file values. Incompatible
with `--generate-config`, `--task-config`, `--solver-config`.

Schema has no top-level `task_config` key (confirmed against installed
`RunConfigInput.model_json_schema()`). Task params go under `task.args`:

```yaml
task:
  task: inspect_petri/audit
  args: {max_turns: 30}
model_roles:
  auditor: {model: openai/gpt-5.6-luna}
  target:  {model: openai/gpt-5-mini}
  judge:   {model: anthropic/claude-opus-5, config: {temperature: 0.0}}
eval_config: {limit: 5}
```

## Usage and cost

`EvalStats` (`log/_log.py:1103`):
- `stats.model_usage: dict[str, ModelUsage]` — keyed by `provider/model`
- `stats.role_usage: dict[str, ModelUsage]` — keyed by role

`ModelUsage` (`model/_model_output.py:16`): `input_tokens`, `output_tokens`, `total_tokens`,
`input_tokens_cache_write`, `input_tokens_cache_read`, `reasoning_tokens`, `total_cost`.

**`input_tokens` excludes cached tokens.** True input = `input_tokens + cache_read +
cache_write`.

**`total_cost` is `None` unless prices are supplied** — the bundled model DB
(`model/_model_data/*.yml`) contains no cost data. `--cost-limit` therefore never fires
without `--model-cost-config`.

`--model-cost-config <file.yaml>` — `ModelCost` requires all four keys, $/M tokens:

```yaml
openai/gpt-5-mini:
  input: 0.25
  output: 2.00
  input_cache_write: 0.25
  input_cache_read: 0.025
```

`set_model_cost` raises for models absent from the bundled DB (e.g. arbitrary `openai-api/`
endpoints).

No CLI usage summary exists. Read directly:

```bash
inspect log dump --header-only <log>.eval | jq '.stats.role_usage'
```

`inspect log` subcommands: `list`, `dump`, `convert`, `schema`, `export-config`, `recover`.

## `inspect score`

`--model-role` overrides are merged over the roles recorded in the log (`_cli/score.py:66`).
Re-runs the scorer only — no target or auditor generation.

```bash
inspect score <log>.eval \
  --model-role 'judge=openai/gpt-5.6-sol' \
  --action append \
  --output-file <log>-judge-sol.eval
```

`--action`: `append` (keep both score sets) | `overwrite`. Scorer is recovered from the log;
`--scorer` unnecessary. Other options: `--model`, `--model-base-url`, `-S`, `--metric`,
`--overwrite`, `--stream`.

## Flags

| Flag | Semantics |
|---|---|
| `--limit` | `10` = count; `10-20` = 1-based inclusive range |
| `--epochs` | repeat dataset; default 1 |
| `--token-limit` | per-sample cap; `500k`, `1m`, `output:1m`, or formula |
| `--message-limit` / `--turn-limit` | per-sample message / generation caps |
| `--cost-limit` | inert without `--model-cost-config` |
| `--max-connections` | default 10 |
| `--adaptive-connections` | default **true** (min 10, start 20, max 100); can exceed `--max-connections` |
| `--max-retries` | default unlimited |
| `--retry-on-error` | sample-level retry; default none |
| `--fail-on-error` | `<1` proportion, `>1` count; default fails on any error |
| `--log-dir` | default `./logs` |

## Third-party providers

**`openai-api/<service>/<model>`** — env vars derive from the service name, uppercased,
hyphens → underscores (`_providers/openai_compatible.py:95`): service `muse` →
`MUSE_API_KEY` + `MUSE_BASE_URL`. Both required; no default base URL.

**`openrouter/<vendor>/<model>`** — `OPENROUTER_API_KEY`; base URL defaults to
`https://openrouter.ai/api/v1`. Anthropic caching on by default for `openrouter/anthropic/*`
(`-M cache_prompt=false` to disable); cache markers are absent from the `.eval` log.

**`google/<model>`** — `GOOGLE_API_KEY` (`GEMINI_API_KEY` honored by the SDK as fallback).

Model args for weak tool-calling endpoints: `-M emulate_tools=true` (synthesizes tool calls
in-prompt), `-M strict_tools=false` (endpoints rejecting `strict` on function schemas).
