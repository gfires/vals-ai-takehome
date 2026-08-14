#!/usr/bin/env python3
"""Paired vertical bar chart: Haiku vs GPT mean scores on top dimensions,
with 80% bootstrap CIs. Luna judge only (n=12 seeds)."""

import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["CMU Serif", "Computer Modern Roman", "STIX", "Times New Roman"],
    "mathtext.fontset": "cm",
    "font.size": 13,
})

HERE = pathlib.Path(__file__).parent
CSV = HERE / "scores.csv"
OUT_PNG = HERE / "dimensions_paired.png"
OUT_PDF = HERE / "dimensions_paired.pdf"

MIN_DIFF = 0.75
N_BOOT = 10_000
CI_LEVEL = 0.80
RNG = np.random.default_rng(42)

BAR_WIDTH = 0.35
COLOR_GPT = "black"
COLOR_HAIKU = "#e67e22"

DIM_LABELS = {
    "overrefusal": "Overrefusal",
    "disappointing": "Disappointing",
    "needs_attention": "Needs attention",
    "unprompted_leaking": "Unprompted leaking",
    "audit_situational_awareness": "Audit sit. awareness",
    "eval_awareness": "Eval awareness",
    "user_over_sysprompt": "User over sysprompt",
    "concerning": "Concerning",
    "unprompted_whistleblowing": "Unprompted whistleblowing",
    "facilitating_terrorism": "Facilitating terrorism",
    "input_hallucination": "Input hallucination",
    "unprompted_initiative": "Unprompted initiative",
    "scenario_realism": "Scenario realism",
    "concerning_with_no_mitigating_factors": "Concerning (no mitigating)",
    "stuck_in_loops": "Stuck in loops",
    "unfaithful_thinking": "Unfaithful thinking",
    "unprompted_self_preservation": "Self-preservation",
}


def bootstrap_ci(values, ci=CI_LEVEL, n_boot=N_BOOT):
    vals = np.asarray(values, dtype=float)
    means = np.array([RNG.choice(vals, size=len(vals), replace=True).mean()
                       for _ in range(n_boot)])
    alpha = (1 - ci) / 2
    lo, hi = np.quantile(means, [alpha, 1 - alpha])
    return lo, hi


def main():
    df = pd.read_csv(CSV)
    luna = df[df["judge"] == "gpt-5.6-luna"].copy()

    score_cols = [c for c in luna.columns if c not in ("seed", "target", "judge")]

    haiku = luna[luna["target"] == "claude-haiku-4-5"].set_index("seed")[score_cols]
    gpt = luna[luna["target"] == "gpt-5-mini"].set_index("seed")[score_cols]

    common_seeds = sorted(set(haiku.index) & set(gpt.index))
    haiku = haiku.loc[common_seeds]
    gpt = gpt.loc[common_seeds]

    diffs = (haiku.mean() - gpt.mean()).abs()
    top_dims = diffs[diffs >= MIN_DIFF].sort_values(ascending=False).index.tolist()

    if not top_dims:
        print(f"No dimensions with |diff| >= {MIN_DIFF}")
        return

    n_dims = len(top_dims)
    fig, ax = plt.subplots(figsize=(max(8, 0.9 * n_dims + 2), 4.5))

    x_positions = np.arange(n_dims)

    for i, dim in enumerate(top_dims):
        h_vals = haiku[dim].values.astype(float)
        g_vals = gpt[dim].values.astype(float)

        h_mean = h_vals.mean()
        g_mean = g_vals.mean()
        h_lo, h_hi = bootstrap_ci(h_vals)
        g_lo, g_hi = bootstrap_ci(g_vals)

        x_g = x_positions[i] - BAR_WIDTH / 2
        x_h = x_positions[i] + BAR_WIDTH / 2

        ax.bar(x_g, g_mean, width=BAR_WIDTH, color=COLOR_GPT, alpha=0.85,
               zorder=2, edgecolor="white", linewidth=0.5)
        ax.bar(x_h, h_mean, width=BAR_WIDTH, color=COLOR_HAIKU, alpha=0.85,
               zorder=2, edgecolor="white", linewidth=0.5)

        ax.errorbar(x_g, g_mean, yerr=[[g_mean - g_lo], [g_hi - g_mean]],
                     fmt="none", ecolor=COLOR_GPT, elinewidth=1.5, capsize=3,
                     capthick=1.2, zorder=3)
        ax.errorbar(x_h, h_mean, yerr=[[h_mean - h_lo], [h_hi - h_mean]],
                     fmt="none", ecolor=COLOR_HAIKU, elinewidth=1.5, capsize=3,
                     capthick=1.2, zorder=3)

    ax.set_xticks(x_positions)
    ax.set_xticklabels([DIM_LABELS.get(d, d) for d in top_dims],
                        rotation=40, ha="right")
    ax.set_ylabel("Mean score (n = 12 seeds)")
    ax.set_ylim(0, 10)
    ax.yaxis.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)

    ax.text(0.5, 1.10, "Fig. 1: Petri Safety Audit, GPT-5-mini vs Haiku 4.5",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=18, fontweight="bold")
    ax.text(0.5, 1.02, "Higher = more problematic  •  80% bootstrap CI  •  Luna judge",
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=13, color="black")

    handles = [
        mlines.Line2D([], [], color=COLOR_GPT, marker="s", markersize=8,
                       markerfacecolor=COLOR_GPT, linestyle="None",
                       label="GPT-5-mini"),
        mlines.Line2D([], [], color=COLOR_HAIKU, marker="s", markersize=8,
                       markerfacecolor=COLOR_HAIKU, linestyle="None",
                       label="Haiku 4.5"),
    ]
    ax.legend(handles=handles, loc="upper right", framealpha=0.9)

    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
    fig.savefig(OUT_PDF, bbox_inches="tight")
    print(f"Saved {OUT_PNG} and {OUT_PDF}")


if __name__ == "__main__":
    main()
