"""
Latency comparison across packet sizes and bitrates.

Expected filename format:
    packet_size_<SIZE>B_<BITRATE>kb<timestamp>.csv

Columns (no header):
    test_num, packet_size_B, RTT_us, one_way_us
"""

import os
import re
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
# Resolves to the folder the script itself lives in, regardless of where you
# run it from. If your CSVs are somewhere else, set an absolute path instead,
# e.g. DATA_DIR = r"C:\data\tests"
DATA_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = DATA_DIR   # plots saved alongside the CSVs

PACKET_SIZES = [5, 16, 32, 48, 64]          # bytes
BITRATES     = [9.6, 57.6, 115.2]           # kbps

# Consistent colour per packet size; markers per bitrate
COLORS  = {5: "#2196F3", 16: "#4CAF50", 32: "#FF9800", 48: "#9C27B0", 64: "#F44336"}
MARKERS = {9.6: "o", 57.6: "s", 115.2: "^"}
LINESTYLES = {9.6: "-", 57.6: "--", 115.2: ":"}

# ── Helpers ────────────────────────────────────────────────────────────────────
def parse_filename(path: str):
    """Return (packet_size_int, bitrate_float) or None if pattern doesn't match."""
    name = Path(path).stem
    m = re.search(r'packet_size_(\d+)B_([\d._]+)kb', name)
    if m:
        bitrate = float(m.group(2).replace("_", "."))
        return int(m.group(1)), bitrate
    return None


def load_all_csvs(data_dir: str):
    """Load every matching CSV into a dict keyed by (packet_size, bitrate)."""
    pattern = os.path.join(data_dir, "packet_size_*.csv")
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError(
            f"No CSV files matching 'packet_size_*.csv' found in: {os.path.abspath(data_dir)}\n"
            "Check DATA_DIR at the top of the script."
        )

    data = {}
    for f in sorted(files):
        key = parse_filename(f)
        if key is None:
            print(f"  [skip] Filename not recognised: {f}")
            continue
        # Files have a header row; read it, then normalise column names
        df = pd.read_csv(f)
        df.columns = ["test_num", "packet_size_B", "RTT_us", "one_way_us"]
        # Remove obvious outliers (RTT > 5× median) — keeps plots clean
        median_rtt = df["RTT_us"].median()
        df = df[df["RTT_us"] < 5 * median_rtt]
        data[key] = df
        print(f"  Loaded {Path(f).name:50s}  n={len(df):4d}  "
              f"median RTT={median_rtt/1000:.2f} ms")

    return data


def summary_table(data: dict):
    """Return a tidy DataFrame with per-config statistics."""
    rows = []
    for (ps, br), df in sorted(data.items()):
        rows.append({
            "Packet size (B)":  ps,
            "Bitrate (kbps)":   br,
            "n":                len(df),
            "RTT mean (ms)":    df["RTT_us"].mean()    / 1000,
            "RTT median (ms)":  df["RTT_us"].median()  / 1000,
            "RTT std (ms)":     df["RTT_us"].std()     / 1000,
            "RTT 95th (ms)":    df["RTT_us"].quantile(0.95) / 1000,
            "OWL mean (ms)":    df["one_way_us"].mean()    / 1000,
            "OWL median (ms)":  df["one_way_us"].median()  / 1000,
            "OWL std (ms)":     df["one_way_us"].std()     / 1000,
        })
    return pd.DataFrame(rows)


# ── Plot 1 – Median RTT vs Packet Size (one line per bitrate) ─────────────────
def plot_rtt_vs_packet_size(stats: pd.DataFrame, out_dir: str):
    fig, ax = plt.subplots(figsize=(8, 5))

    for br in sorted(stats["Bitrate (kbps)"].unique()):
        sub = stats[stats["Bitrate (kbps)"] == br].sort_values("Packet size (B)")
        ax.plot(
            sub["Packet size (B)"], sub["RTT median (ms)"],
            marker=MARKERS[br], linestyle=LINESTYLES[br],
            linewidth=1.8, markersize=7,
            label=f"{br} kbps",
        )
        # ±1 std shading
        ax.fill_between(
            sub["Packet size (B)"],
            sub["RTT median (ms)"] - sub["RTT std (ms)"],
            sub["RTT median (ms)"] + sub["RTT std (ms)"],
            alpha=0.10,
        )

    ax.set_xlabel("Packet Size (bytes)", fontsize=11)
    ax.set_ylabel("Median RTT (ms)", fontsize=11)
    ax.set_title("Round-Trip Time vs Packet Size\n(shading = ±1 σ)", fontsize=12)
    ax.set_xticks(PACKET_SIZES)
    ax.legend(title="Bitrate", framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    fig.tight_layout()
    out = os.path.join(out_dir, "plot_rtt_vs_packet_size.png")
    fig.savefig(out, dpi=150)
    print(f"  Saved: {out}")
    plt.close(fig)


# ── Plot 2 – Median one-way latency vs Packet Size ───────────────────────────
def plot_owl_vs_packet_size(stats: pd.DataFrame, out_dir: str):
    fig, ax = plt.subplots(figsize=(8, 5))

    for br in sorted(stats["Bitrate (kbps)"].unique()):
        sub = stats[stats["Bitrate (kbps)"] == br].sort_values("Packet size (B)")
        ax.plot(
            sub["Packet size (B)"], sub["OWL median (ms)"],
            marker=MARKERS[br], linestyle=LINESTYLES[br],
            linewidth=1.8, markersize=7,
            label=f"{br} kbps",
        )
        ax.fill_between(
            sub["Packet size (B)"],
            sub["OWL median (ms)"] - sub["OWL std (ms)"],
            sub["OWL median (ms)"] + sub["OWL std (ms)"],
            alpha=0.10,
        )

    ax.set_xlabel("Packet Size (bytes)", fontsize=11)
    ax.set_ylabel("Median One-Way Latency (ms)", fontsize=11)
    ax.set_title("One-Way Latency vs Packet Size\n(shading = ±1 σ)", fontsize=12)
    ax.set_xticks(PACKET_SIZES)
    ax.legend(title="Bitrate", framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    fig.tight_layout()
    out = os.path.join(out_dir, "plot_owl_vs_packet_size.png")
    fig.savefig(out, dpi=150)
    print(f"  Saved: {out}")
    plt.close(fig)


# ── Plot 3 – Grouped bar chart: median RTT for all combos ────────────────────
def plot_grouped_bar(stats: pd.DataFrame, out_dir: str):
    bitrates     = sorted(stats["Bitrate (kbps)"].unique())
    packet_sizes = sorted(stats["Packet size (B)"].unique())
    n_br  = len(bitrates)
    n_ps  = len(packet_sizes)
    x     = np.arange(n_ps)
    width = 0.7 / n_br
    offsets = np.linspace(-(n_br - 1) / 2, (n_br - 1) / 2, n_br) * width

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=False)

    for ax, metric, col, ylabel in [
        (axes[0], "RTT median (ms)",  "RTT",  "Median RTT (ms)"),
        (axes[1], "OWL median (ms)", "OWL", "Median One-Way Latency (ms)"),
    ]:
        for i, br in enumerate(bitrates):
            sub = stats[stats["Bitrate (kbps)"] == br].sort_values("Packet size (B)")
            vals = [sub[sub["Packet size (B)"] == ps][metric].values[0]
                    if len(sub[sub["Packet size (B)"] == ps]) else 0
                    for ps in packet_sizes]
            std_col = metric.replace("median", "std")
            errs = [sub[sub["Packet size (B)"] == ps][std_col].values[0]
                    if len(sub[sub["Packet size (B)"] == ps]) else 0
                    for ps in packet_sizes]
            ax.bar(x + offsets[i], vals, width, yerr=errs,
                   label=f"{br} kbps", capsize=3, error_kw={"linewidth": 1})

        ax.set_xlabel("Packet Size (bytes)", fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(ylabel, fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{ps} B" for ps in packet_sizes])
        ax.legend(title="Bitrate", fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    fig.suptitle("Latency Comparison — All Packet Sizes and Bitrates\n(error bars = ±1 σ)",
                 fontsize=13, y=1.01)
    fig.tight_layout()
    out = os.path.join(out_dir, "plot_grouped_bar.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"  Saved: {out}")
    plt.close(fig)


# ── Plot 4 – Box plot distribution per configuration ─────────────────────────
def plot_boxplot(data: dict, out_dir: str):
    """One box per (bitrate, packet_size) combo, grouped by bitrate."""
    bitrates     = sorted({k[1] for k in data})
    packet_sizes = sorted({k[0] for k in data})

    fig, axes = plt.subplots(1, len(bitrates), figsize=(5 * len(bitrates), 5),
                              sharey=True)
    if len(bitrates) == 1:
        axes = [axes]

    for ax, br in zip(axes, bitrates):
        groups = []
        labels = []
        for ps in packet_sizes:
            if (ps, br) in data:
                groups.append(data[(ps, br)]["RTT_us"].values / 1000)
                labels.append(f"{ps} B")

        bp = ax.boxplot(groups, labels=labels, patch_artist=True,
                        medianprops={"color": "black", "linewidth": 2},
                        flierprops={"marker": ".", "markersize": 3, "alpha": 0.4})
        for patch, ps in zip(bp["boxes"], packet_sizes):
            patch.set_facecolor(COLORS.get(ps, "#888"))
            patch.set_alpha(0.75)

        ax.set_title(f"{br} kbps", fontsize=11)
        ax.set_xlabel("Packet Size", fontsize=10)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    axes[0].set_ylabel("RTT (ms)", fontsize=11)
    fig.suptitle("RTT Distribution — Grouped by Bitrate", fontsize=13)
    fig.tight_layout()
    out = os.path.join(out_dir, "plot_boxplot_rtt.png")
    fig.savefig(out, dpi=150)
    print(f"  Saved: {out}")
    plt.close(fig)


# ── Plot 5 – Heatmap: median RTT (packet size × bitrate) ─────────────────────
def plot_heatmap(stats: pd.DataFrame, out_dir: str):
    import matplotlib.colors as mcolors

    for metric, title, fname in [
        ("RTT median (ms)",  "Median RTT (ms)",             "plot_heatmap_rtt.png"),
        ("OWL median (ms)", "Median One-Way Latency (ms)", "plot_heatmap_owl.png"),
    ]:
        pivot = stats.pivot(index="Packet size (B)", columns="Bitrate (kbps)", values=metric)

        fig, ax = plt.subplots(figsize=(6, 4))
        im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd",
                       norm=mcolors.Normalize(vmin=pivot.values.min(),
                                              vmax=pivot.values.max()))

        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([f"{c} kbps" for c in pivot.columns])
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels([f"{r} B" for r in pivot.index])
        ax.set_xlabel("Bitrate", fontsize=11)
        ax.set_ylabel("Packet Size", fontsize=11)
        ax.set_title(f"Heatmap — {title}", fontsize=12)

        # Annotate cells
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.values[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                            fontsize=9,
                            color="white" if val > pivot.values.max() * 0.65 else "black")

        plt.colorbar(im, ax=ax, label=title)
        fig.tight_layout()
        out = os.path.join(out_dir, fname)
        fig.savefig(out, dpi=150)
        print(f"  Saved: {out}")
        plt.close(fig)


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Loading data ===")
    data = load_all_csvs(DATA_DIR)

    print("\n=== Computing statistics ===")
    stats = summary_table(data)
    print(stats.to_string(index=False))

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n=== Generating plots ===")
    plot_rtt_vs_packet_size(stats, OUTPUT_DIR)
    plot_owl_vs_packet_size(stats, OUTPUT_DIR)
    plot_grouped_bar(stats, OUTPUT_DIR)
    plot_boxplot(data, OUTPUT_DIR)
    plot_heatmap(stats, OUTPUT_DIR)

    print("\nDone. All plots saved to:", os.path.abspath(OUTPUT_DIR))
