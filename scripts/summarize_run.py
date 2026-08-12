#!/usr/bin/env python3
"""Generate a human-readable summary.md next to a Petri .eval log's JSON dump.

Usage: summarize_run.py <run.json> [<run.json> ...]
Each <run.json> must be a full `inspect log dump --resolve-attachments full`
output. Writes <run>.summary.md alongside it.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
from cost_report import cost_for, load_prices  # noqa: E402

DIMENSIONS_DIR = (
    Path(__file__).resolve().parent.parent
    / ".venv/lib/python3.12/site-packages/inspect_petri/_judge/dimensions"
)


def load_palettes():
    palettes = {}
    if not DIMENSIONS_DIR.is_dir():
        return palettes
    for f in DIMENSIONS_DIR.glob("*.md"):
        text = f.read_text()
        palette = "good-low"
        if "palette: good-high" in text:
            palette = "good-high"
        elif "palette: neutral" in text:
            palette = "neutral"
        elif "palette: diverging" in text:
            palette = "diverging"
        palettes[f.stem] = palette
    return palettes


def fmt_score_row(dim, score, palette):
    flag = ""
    if palette == "good-low" and score >= 5:
        flag = " ⚠️"
    elif palette == "good-high" and score <= 3:
        flag = " ⚠️"
    return f"| {dim} | {score} | {palette} |{flag}"


def summarize_sample(sample, palettes):
    lines = []
    sid = sample.get("id", "unknown")
    lines.append(f"### Sample `{sid}`")
    lines.append("")

    meta = sample.get("metadata", {}) or {}
    tags = meta.get("tags")
    if tags:
        lines.append(f"Tags: {', '.join(tags)}")
        lines.append("")

    scores = sample.get("scores", {}).get("audit_judge", {})
    value = scores.get("value", {}) or {}
    smeta = scores.get("metadata", {}) or {}

    concerning = value.get("concerning")
    if concerning is not None:
        lines.append(f"**concerning (headline): {concerning}/10**")
        lines.append("")

    summary_text = smeta.get("summary")
    if summary_text:
        lines.append("**Judge summary:**")
        lines.append("")
        lines.append(summary_text.strip())
        lines.append("")

    highlights = smeta.get("highlights")
    if highlights:
        lines.append("**Highlights:**")
        lines.append("")
        lines.append(str(highlights).strip())
        lines.append("")

    if value:
        lines.append("**Scores** (sorted worst-first by direction; ⚠️ = score is on the bad side):")
        lines.append("")
        lines.append("| dimension | score | palette |")
        lines.append("|---|---|---|")

        def badness(item):
            dim, score = item
            palette = palettes.get(dim, "good-low")
            if palette == "good-high":
                return -score
            if palette == "good-low":
                return score
            return -99  # neutral/diverging: no direction, sort last

        for dim, score in sorted(value.items(), key=badness, reverse=True):
            palette = palettes.get(dim, "good-low")
            lines.append(fmt_score_row(dim, score, palette))
        lines.append("")

    turn_count = sample.get("turn_count")
    total_time = sample.get("total_time")
    if turn_count is not None or total_time is not None:
        lines.append(f"Turns: {turn_count}  ·  Wall time: {total_time:.1f}s" if total_time else f"Turns: {turn_count}")
        lines.append("")

    return "\n".join(lines)


def summarize_run(json_path: Path, palettes):
    with open(json_path) as f:
        data = json.load(f)

    ev = data.get("eval", {})
    stats = data.get("stats", {})
    role_usage = stats.get("role_usage", {})
    model_roles = ev.get("model_roles") or {}
    prices = load_prices()

    lines = []
    lines.append(f"# Run summary: {json_path.stem}")
    lines.append("")
    lines.append(f"Status: **{data.get('status')}**")
    lines.append(f"Task: `{ev.get('task')}`")

    if model_roles:
        role_strs = [f"{r}={cfg.get('model', cfg) if isinstance(cfg, dict) else cfg}" for r, cfg in model_roles.items()]
        lines.append(f"Roles: {', '.join(role_strs)}")
    lines.append("")

    lines.append("## Cost")
    lines.append("")
    lines.append("| role | input | output | cache_read | cache_write | cost |")
    lines.append("|---|---|---|---|---|---|")
    total_cost = 0.0
    for role, u in role_usage.items():
        model = model_roles.get(role, {}).get("model")
        cost = cost_for(model, u, prices) if model else 0.0
        total_cost += cost
        lines.append(
            f"| {role} | {u.get('input_tokens', 0)} | {u.get('output_tokens', 0)} | "
            f"{u.get('input_tokens_cache_read', 0)} | {u.get('input_tokens_cache_write', 0)} | ${cost:.4f} |"
        )
    lines.append(f"| **total** | | | | | **${total_cost:.4f}** |")
    lines.append("")

    samples = data.get("samples", [])
    lines.append(f"## Samples ({len(samples)})")
    lines.append("")
    for sample in samples:
        lines.append(summarize_sample(sample, palettes))
        lines.append("---")
        lines.append("")

    eval_path = json_path.with_suffix(".eval")
    lines.append(f"Full transcript: `inspect view --log-dir {eval_path.parent}` (select this run), or read `{json_path.name}` directly.")
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    palettes = load_palettes()

    for arg in sys.argv[1:]:
        json_path = Path(arg)
        summary = summarize_run(json_path, palettes)
        out_path = json_path.with_suffix("").with_suffix(".summary.md")
        out_path.write_text(summary)
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
