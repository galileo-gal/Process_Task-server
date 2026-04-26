# experiments/analysis/plot.py
"""
Generate experiment plots from results/summary.csv.

Usage:
    python experiments/analysis/plot.py
    python experiments/analysis/plot.py --summary results/summary.csv --out results/plots/

Produces 5 charts:
    1. waiting_time_by_scheduler.png
    2. execution_time_by_executor.png
    3. ctx_switches_by_executor.png
    4. memory_delta_by_workload.png
    5. total_time_heatmap.png
"""
import argparse
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # safe for headless / WSL
import matplotlib.pyplot as plt

WORKLOAD_ORDER = [
    "cpu_fibonacci", "cpu_matrix", "cpu_prime",
    "io_sleep", "io_file",
    "memory_numpy", "memory_list",
    "mixed_cpu_io",
    "ml_predict",
]


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df[df["error"].isna()].copy()


def save(fig, out_dir: str, name: str):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved → {path}")


def plot_waiting_by_scheduler(df, out_dir):
    pivot = (
        df.groupby(["scheduler", "workload_type"])["waiting_time"]
        .mean().unstack("scheduler").reindex(WORKLOAD_ORDER)
    )
    fig, ax = plt.subplots(figsize=(12, 5))
    pivot.plot(kind="bar", ax=ax, width=0.7)
    ax.set_title("Mean Waiting Time — FIFO vs Priority (per workload)")
    ax.set_ylabel("Waiting Time (s)")
    ax.set_xlabel("Workload Type")
    ax.tick_params(axis="x", rotation=30)
    ax.legend(title="Scheduler")
    save(fig, out_dir, "waiting_time_by_scheduler.png")


def plot_execution_by_executor(df, out_dir):
    pivot = (
        df.groupby(["executor", "workload_type"])["execution_time"]
        .mean().unstack("executor").reindex(WORKLOAD_ORDER)
    )
    fig, ax = plt.subplots(figsize=(12, 5))
    pivot.plot(kind="bar", ax=ax, width=0.7)
    ax.set_title("Mean Execution Time — by Executor (per workload)")
    ax.set_ylabel("Execution Time (s)")
    ax.set_xlabel("Workload Type")
    ax.tick_params(axis="x", rotation=30)
    ax.legend(title="Executor")
    save(fig, out_dir, "execution_time_by_executor.png")


def plot_ctx_switches(df, out_dir):
    pivot = (
        df.groupby("executor")[["ctx_voluntary_delta", "ctx_involuntary_delta"]]
        .mean().round(2)
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    pivot.plot(kind="bar", ax=ax, width=0.5)
    ax.set_title("Mean Context Switches per Job — by Executor")
    ax.set_ylabel("Context Switches (delta)")
    ax.set_xlabel("Executor")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(["Voluntary", "Involuntary"])
    save(fig, out_dir, "ctx_switches_by_executor.png")


def plot_memory_delta(df, out_dir):
    pivot = (
        df.groupby("workload_type")["memory_delta_mb"]
        .mean().reindex(WORKLOAD_ORDER)
    )
    fig, ax = plt.subplots(figsize=(12, 5))
    pivot.plot(kind="bar", ax=ax, color="steelblue", width=0.6)
    ax.set_title("Mean Memory Delta per Job — by Workload")
    ax.set_ylabel("Memory Delta (MB)")
    ax.set_xlabel("Workload Type")
    ax.tick_params(axis="x", rotation=30)
    ax.axhline(0, color="black", linewidth=0.8)
    save(fig, out_dir, "memory_delta_by_workload.png")


def plot_total_time_heatmap(df, out_dir):
    pivot = (
        df.groupby(["executor", "scheduler"])["total_time"]
        .mean().unstack("scheduler")
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_yticks(range(len(pivot.index)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticklabels(pivot.index)
    ax.set_title("Mean Total Time (s) — Executor × Scheduler")
    plt.colorbar(im, ax=ax, label="Total Time (s)")
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=9, color="black")
    save(fig, out_dir, "total_time_heatmap.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", default="results/summary.csv")
    parser.add_argument("--out",     default="results/plots")
    args = parser.parse_args()

    if not os.path.exists(args.summary):
        print(f"Not found: {args.summary} — run summarize.py first.")
        return

    df = load(args.summary)
    print(f"Loaded {len(df)} rows from {args.summary}")

    plot_waiting_by_scheduler(df, args.out)
    plot_execution_by_executor(df, args.out)
    plot_ctx_switches(df, args.out)
    plot_memory_delta(df, args.out)
    plot_total_time_heatmap(df, args.out)

    print(f"\nAll plots → {args.out}/")


if __name__ == "__main__":
    main()
