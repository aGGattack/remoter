"""
Latency vs Bitrate — fixed packet size (5 B).

Loads all CSVs matching: latency_*kbps*.csv
Each file contains measurements for one bitrate.

Columns: Sample, Bitrate (string e.g. "1.2 kbps"), RTT_us, OneWayLatency_ms
"""

import os
import re
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────
DATA_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = DATA_DIR

PACKET_SIZE_B = 5   # bytes — for axis/title labelling only

# Expected bitrates in ascending order — used to sort x-axis correctly
BITRATE_ORDER = [1.2, 9.6, 57.6, 115.2, 250.0]

# ── Load ────────────────────────────────────────────────────────────────────────
def load_all_csvs(data_dir: str) -> pd.DataFrame:
    pattern = os.path.join(data_dir, "latency_*kbps*.csv")
    files   = glob.glob(pattern)

    if not files:
        raise FileNotFoundError(
            f"No CSV files matching 'latency_*kbps*.csv' found in:\n"
            f"  {os.path.abspath(data_dir)}\n"
            "Check DATA_DIR at the top of the script."
        )

    frames = []
    for f in sorted(files):
        df = pd.read_csv(f)
        # Normalise column names regardless of capitalisation or spacing
        df.columns = [c.strip() for c in df.columns]
        col_map = {c: ["sample", "bitrate_str", "RTT_us", "OWL_ms"][i]
                   for i, c in enumerate(df.columns)}
        df = df.rename(columns=col_map)
        frames.append(df)
        print(f"  Loaded {Path(f).name:50s}  n={len(df):4d}")

    combined = pd.concat(frames, ignore_index=True)

    # Parse numeric bitrate from strings like "1.2 kbps" or "57.6kbps"
    combined["bitrate_kbps"] = (
        combined["bitrate_str"]
        .str.extract(r"([\d.]+)")
        .astype(float)
    )
    return combined


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Drop RTT values above 5× the per-bitrate median."""
    clean_groups = []
    for br, g in df.groupby("bitrate_kbps"):
        med = g["RTT_us"].median()
        clean_groups.append(g[g["RTT_us"] < 5 * med])
    return pd.concat(clean_groups, ignore_index=True)


def build_stats(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("bitrate_kbps")["RTT_us"]
    stats = pd.DataFrame({
        "n":           g.count(),
        "mean_ms":     g.mean()              / 1000,
        "median_ms":   g.median()            / 1000,
        "std_ms":      g.std()               / 1000,
        "p5_ms":       g.quantile(0.05)      / 1000,
        "p95_ms":      g.quantile(0.95)      / 1000,
    }).reset_index()

    # Sort by the known bitrate order; unknowns go to the end
    order_map = {b: i for i, b in enumerate(BITRATE_ORDER)}
    stats["_order"] = stats["bitrate_kbps"].map(order_map).fillna(999)
    stats = stats.sort_values("_order").drop(columns="_order").reset_index(drop=True)
    return stats


# ── Plot 1 — Median RTT with 5th–95th percentile band ─────────────────────────
def plot_rtt_line(stats: pd.DataFrame, out_dir: str):
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(stats["bitrate_kbps"], stats["median_ms"],
            color="#2196F3", marker="o", linewidth=2, markersize=7, zorder=3,
            label="Median RTT")
    ax.fill_between(stats["bitrate_kbps"],
                    stats["p5_ms"], stats["p95_ms"],
                    alpha=0.15, color="#2196F3", label="5th–95th percentile")
    ax.fill_between(stats["bitrate_kbps"],
                    stats["median_ms"] - stats["std_ms"],
                    stats["median_ms"] + stats["std_ms"],
                    alpha=0.25, color="#2196F3", label="±1 σ")

    # Annotate each point with its median value
    for _, row in stats.iterrows():
        ax.annotate(f"{row['median_ms']:.1f} ms",
                    xy=(row["bitrate_kbps"], row["median_ms"]),
                    xytext=(0, 10), textcoords="offset points",
                    ha="center", fontsize=8, color="#1565C0")

    ax.set_xscale("log")
    ax.set_xlabel("Bitrate (kbps)", fontsize=11)
    ax.set_ylabel("RTT (ms)", fontsize=11)
    ax.set_title(f"Round-Trip Time vs Bitrate  |  Packet size = {PACKET_SIZE_B} B",
                 fontsize=12)
    ax.set_xticks(stats["bitrate_kbps"])
    ax.set_xticklabels([f"{b:g}" for b in stats["bitrate_kbps"]])
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())
    ax.legend(fontsize=9)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)

    fig.tight_layout()
    out = os.path.join(out_dir, "plot_rtt_vs_bitrate.png")
    fig.savefig(out, dpi=150)
    print(f"  Saved: {out}")
    plt.close(fig)


# ── Plot 2 — One-way latency line ──────────────────────────────────────────────
def plot_owl_line(df: pd.DataFrame, stats: pd.DataFrame, out_dir: str):
    # OWL stats (already in ms in the CSV)
    owl = df.groupby("bitrate_kbps")["OWL_ms"]
    owl_stats = pd.DataFrame({
        "median_ms": owl.median(),
        "std_ms":    owl.std(),
        "p5_ms":     owl.quantile(0.05),
        "p95_ms":    owl.quantile(0.95),
    }).reset_index()
    order_map = {b: i for i, b in enumerate(BITRATE_ORDER)}
    owl_stats["_order"] = owl_stats["bitrate_kbps"].map(order_map).fillna(999)
    owl_stats = owl_stats.sort_values("_order").drop(columns="_order").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(owl_stats["bitrate_kbps"], owl_stats["median_ms"],
            color="#4CAF50", marker="s", linewidth=2, markersize=7, zorder=3,
            label="Median one-way latency")
    ax.fill_between(owl_stats["bitrate_kbps"],
                    owl_stats["median_ms"] - owl_stats["std_ms"],
                    owl_stats["median_ms"] + owl_stats["std_ms"],
                    alpha=0.25, color="#4CAF50", label="±1 σ")

    for _, row in owl_stats.iterrows():
        ax.annotate(f"{row['median_ms']:.1f} ms",
                    xy=(row["bitrate_kbps"], row["median_ms"]),
                    xytext=(0, 10), textcoords="offset points",
                    ha="center", fontsize=8, color="#2E7D32")

    ax.set_xscale("log")
    ax.set_xlabel("Bitrate (kbps)", fontsize=11)
    ax.set_ylabel("One-Way Latency (ms)", fontsize=11)
    ax.set_title(f"One-Way Latency vs Bitrate  |  Packet size = {PACKET_SIZE_B} B",
                 fontsize=12)
    ax.set_xticks(owl_stats["bitrate_kbps"])
    ax.set_xticklabels([f"{b:g}" for b in owl_stats["bitrate_kbps"]])
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())
    ax.legend(fontsize=9)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)

    fig.tight_layout()
    out = os.path.join(out_dir, "plot_owl_vs_bitrate.png")
    fig.savefig(out, dpi=150)
    print(f"  Saved: {out}")
    plt.close(fig)


# ── Plot 3 — Box plot, one box per bitrate ─────────────────────────────────────
def plot_boxplot(df: pd.DataFrame, stats: pd.DataFrame, out_dir: str):
    bitrates = stats["bitrate_kbps"].tolist()
    groups   = [df[df["bitrate_kbps"] == br]["RTT_us"].values / 1000
                for br in bitrates]
    labels   = [f"{b:g} kbps" for b in bitrates]

    fig, ax = plt.subplots(figsize=(9, 5))

    bp = ax.boxplot(groups, tick_labels=labels, patch_artist=True,
                    medianprops={"color": "black", "linewidth": 2},
                    flierprops={"marker": ".", "markersize": 4, "alpha": 0.4})

    colors = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#F44336"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_xlabel("Bitrate", fontsize=11)
    ax.set_ylabel("RTT (ms)", fontsize=11)
    ax.set_title(f"RTT Distribution per Bitrate  |  Packet size = {PACKET_SIZE_B} B",
                 fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    fig.tight_layout()
    out = os.path.join(out_dir, "plot_boxplot_bitrate.png")
    fig.savefig(out, dpi=150)
    print(f"  Saved: {out}")
    plt.close(fig)


# ── Plot 4 — RTT and OWL side by side bar chart ────────────────────────────────
def plot_bar_comparison(df: pd.DataFrame, stats: pd.DataFrame, out_dir: str):
    bitrates  = stats["bitrate_kbps"].tolist()
    x         = np.arange(len(bitrates))
    owl_med   = [df[df["bitrate_kbps"] == br]["OWL_ms"].median() for br in bitrates]
    owl_std   = [df[df["bitrate_kbps"] == br]["OWL_ms"].std()    for br in bitrates]

    fig, ax = plt.subplots(figsize=(9, 5))

    width = 0.35
    bars_rtt = ax.bar(x - width / 2, stats["median_ms"], width,
                      yerr=stats["std_ms"], capsize=4,
                      color="#2196F3", alpha=0.8, label="RTT (median ±1 σ)")
    bars_owl = ax.bar(x + width / 2, owl_med, width,
                      yerr=owl_std, capsize=4,
                      color="#4CAF50", alpha=0.8, label="One-Way Latency (median ±1 σ)")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{b:g} kbps" for b in bitrates])
    ax.set_xlabel("Bitrate", fontsize=11)
    ax.set_ylabel("Latency (ms)", fontsize=11)
    ax.set_title(f"RTT vs One-Way Latency per Bitrate  |  Packet size = {PACKET_SIZE_B} B",
                 fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    fig.tight_layout()
    out = os.path.join(out_dir, "plot_bar_rtt_owl.png")
    fig.savefig(out, dpi=150)
    print(f"  Saved: {out}")
    plt.close(fig)


# ── Main ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Loading data ===")
    df = load_all_csvs(DATA_DIR)
    df = remove_outliers(df)

    print("\n=== Statistics ===")
    stats = build_stats(df)
    print(stats.to_string(index=False))

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n=== Generating plots ===")
    plot_rtt_line(stats, OUTPUT_DIR)
    plot_owl_line(df, stats, OUTPUT_DIR)
    plot_boxplot(df, stats, OUTPUT_DIR)
    plot_bar_comparison(df, stats, OUTPUT_DIR)

    print("\nDone. All plots saved to:", os.path.abspath(OUTPUT_DIR))
