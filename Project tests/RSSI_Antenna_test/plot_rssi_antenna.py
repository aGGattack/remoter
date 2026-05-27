"""
RSSI vs Distance — comparison across antenna lengths.

Filename format:  rssi_data_*_<LENGTH>cm_<timestamp>.csv
                  e.g. rssi_data_Horizontal_16_5cm_20260521_133144.csv

Columns: Distance_m, Sample_Number, RSSI_dBm

Multiple CSV files for the same length are merged before averaging.
"""

import os
import re
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
from collections import defaultdict

# ── Config ─────────────────────────────────────────────────────────────────────
DATA_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = DATA_DIR

# Known lengths in display order (cm) — edit if you add more
LENGTH_ORDER = [16.5, 16.7, 16.9, 17.1, 17.3, 17.5, 17.8]

# Colourblind-friendly palette, one colour per antenna length
PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
           "#9467bd", "#8c564b", "#e377c2"]

# ── Load ────────────────────────────────────────────────────────────────────────
def parse_length(path: str):
    """Extract antenna length in cm from filename, e.g. '16_5cm' → 16.5"""
    # Matches both 16_5cm and 16.5cm
    m = re.search(r'_([\d]+[_.][\d]+)cm[_.]', Path(path).name)
    if m:
        return float(m.group(1).replace("_", "."))
    # fallback: single integer cm value e.g. 17cm
    m2 = re.search(r'_(\d+)cm[_.]', Path(path).name)
    if m2:
        return float(m2.group(1))
    return None


def load_all(data_dir: str) -> pd.DataFrame:
    pattern = os.path.join(data_dir, "rssi_data_*.csv")
    files   = glob.glob(pattern)

    if not files:
        raise FileNotFoundError(
            f"No files matching 'rssi_data_*.csv' found in:\n"
            f"  {os.path.abspath(data_dir)}\n"
            "Check DATA_DIR at the top of the script."
        )

    by_length = defaultdict(list)
    for f in sorted(files):
        length = parse_length(f)
        if length is None:
            print(f"  [skip] Could not parse length from: {Path(f).name}")
            continue
        df = pd.read_csv(f)
        df.columns = [c.strip() for c in df.columns]
        # Normalise column names regardless of capitalisation
        df = df.rename(columns={c: c.lower().replace(" ", "_") for c in df.columns})
        df = df.rename(columns={"distance_m": "distance", "rssi_dbm": "rssi"})
        df["length_cm"] = length
        by_length[length].append(df)
        print(f"  Loaded {Path(f).name:55s}  length={length} cm  n={len(df)}")

    frames = []
    for length, dfs in sorted(by_length.items()):
        merged = pd.concat(dfs, ignore_index=True)
        frames.append(merged)
        if len(dfs) > 1:
            print(f"  → Merged {len(dfs)} files for {length} cm  (total n={len(merged)})")

    return pd.concat(frames, ignore_index=True)


def build_stats(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["length_cm", "distance"])["rssi"]
    stats = pd.DataFrame({
        "mean":   g.mean(),
        "median": g.median(),
        "std":    g.std(),
        "p5":     g.quantile(0.05),
        "p95":    g.quantile(0.95),
        "n":      g.count(),
    }).reset_index()
    return stats


# ── Plot 1 — Main: median RSSI vs distance, one line per antenna length ────────
def plot_rssi_vs_distance(stats: pd.DataFrame, out_dir: str):
    lengths = sorted(stats["length_cm"].unique(),
                     key=lambda x: LENGTH_ORDER.index(x) if x in LENGTH_ORDER else x)

    fig, ax = plt.subplots(figsize=(9, 6))

    for i, length in enumerate(lengths):
        sub    = stats[stats["length_cm"] == length].sort_values("distance")
        color  = PALETTE[i % len(PALETTE)]
        marker = ["o", "s", "^", "D", "v", "P", "X"][i % 7]

        ax.plot(sub["distance"], sub["median"],
                color=color, marker=marker, linewidth=2, markersize=7,
                label=f"{length} cm", zorder=3)
        ax.fill_between(sub["distance"],
                        sub["p5"], sub["p95"],
                        alpha=0.08, color=color)
        ax.fill_between(sub["distance"],
                        sub["median"] - sub["std"],
                        sub["median"] + sub["std"],
                        alpha=0.15, color=color)

    ax.set_xscale("log")
    ax.set_xlabel("Distance (m)", fontsize=11)
    ax.set_ylabel("RSSI (dBm)", fontsize=11)
    ax.set_title("RSSI vs Distance — Antenna Length Comparison\n"
                 "(shading = ±1 σ  |  band = 5th–95th percentile)", fontsize=12)

    distances = sorted(stats["distance"].unique())
    ax.set_xticks(distances)
    ax.set_xticklabels([f"{d} m" for d in distances])
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())

    ax.legend(title="Antenna length", fontsize=9, title_fontsize=9,
              loc="lower left", framealpha=0.9)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    fig.tight_layout()
    out = os.path.join(out_dir, "plot_rssi_vs_distance.png")
    fig.savefig(out, dpi=150)
    print(f"  Saved: {out}")
    plt.close(fig)


# ── Plot 2 — RSSI at each distance as a bar chart (easy ranking) ───────────────
def plot_bar_per_distance(stats: pd.DataFrame, out_dir: str):
    lengths   = sorted(stats["length_cm"].unique(),
                       key=lambda x: LENGTH_ORDER.index(x) if x in LENGTH_ORDER else x)
    distances = sorted(stats["distance"].unique())
    n_len     = len(lengths)
    x         = np.arange(len(distances))
    width     = 0.7 / n_len
    offsets   = np.linspace(-(n_len - 1) / 2, (n_len - 1) / 2, n_len) * width

    fig, ax = plt.subplots(figsize=(11, 6))

    for i, length in enumerate(lengths):
        sub  = stats[stats["length_cm"] == length].sort_values("distance")
        vals = [sub[sub["distance"] == d]["median"].values[0]
                if len(sub[sub["distance"] == d]) else np.nan
                for d in distances]
        errs = [sub[sub["distance"] == d]["std"].values[0]
                if len(sub[sub["distance"] == d]) else 0
                for d in distances]
        ax.bar(x + offsets[i], vals, width, yerr=errs,
               color=PALETTE[i % len(PALETTE)], alpha=0.8,
               label=f"{length} cm", capsize=3, error_kw={"linewidth": 1})

    ax.set_xticks(x)
    ax.set_xticklabels([f"{d} m" for d in distances])
    ax.set_xlabel("Distance (m)", fontsize=11)
    ax.set_ylabel("Median RSSI (dBm)", fontsize=11)
    ax.set_title("Median RSSI per Distance — Antenna Length Comparison\n"
                 "(error bars = ±1 σ)", fontsize=12)
    ax.legend(title="Antenna length", fontsize=9, title_fontsize=9,
              loc="lower left", framealpha=0.9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    fig.tight_layout()
    out = os.path.join(out_dir, "plot_rssi_bar_per_distance.png")
    fig.savefig(out, dpi=150)
    print(f"  Saved: {out}")
    plt.close(fig)


# ── Plot 3 — Box plots at the longest distance only ────────────────────────────
def plot_boxplot_far(df: pd.DataFrame, out_dir: str):
    max_dist = df["distance"].max()
    sub      = df[df["distance"] == max_dist]
    lengths  = sorted(sub["length_cm"].unique(),
                      key=lambda x: LENGTH_ORDER.index(x) if x in LENGTH_ORDER else x)

    groups = [sub[sub["length_cm"] == l]["rssi"].values for l in lengths]
    labels = [f"{l} cm" for l in lengths]
    colors = PALETTE[:len(lengths)]

    fig, ax = plt.subplots(figsize=(9, 5))
    bp = ax.boxplot(groups, tick_labels=labels, patch_artist=True,
                    medianprops={"color": "black", "linewidth": 2},
                    flierprops={"marker": ".", "markersize": 4, "alpha": 0.5})
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)

    ax.set_xlabel("Antenna Length", fontsize=11)
    ax.set_ylabel("RSSI (dBm)", fontsize=11)
    ax.set_title(f"RSSI Distribution at {max_dist} m — per Antenna Length", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    fig.tight_layout()
    out = os.path.join(out_dir, f"plot_rssi_boxplot_{max_dist}m.png")
    fig.savefig(out, dpi=150)
    print(f"  Saved: {out}")
    plt.close(fig)


# ── Main ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Loading data ===")
    df    = load_all(DATA_DIR)

    print("\n=== Statistics ===")
    stats = build_stats(df)
    pivot = stats.pivot(index="distance", columns="length_cm", values="median").round(1)
    pivot.columns = [f"{c} cm" for c in pivot.columns]
    pivot.index   = [f"{d} m"  for d in pivot.index]
    print("Median RSSI (dBm):")
    print(pivot.to_string())

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n=== Generating plots ===")
    plot_rssi_vs_distance(stats, OUTPUT_DIR)
    plot_bar_per_distance(stats, OUTPUT_DIR)
    plot_boxplot_far(df, OUTPUT_DIR)

    print("\nDone. Plots saved to:", os.path.abspath(OUTPUT_DIR))
