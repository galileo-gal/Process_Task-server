# experiments/analysis/summarize.py
"""
Summarize all experiment JSONL files into a single summary.csv.

Usage:
    python experiments/analysis/summarize.py
    python experiments/analysis/summarize.py --results_dir results/
"""
import argparse
import json
import os
import re
import pandas as pd


def parse_meta(filename: str) -> dict:
    stem = os.path.splitext(os.path.basename(filename))[0]
    match = re.match(r"^(baseline|thread|process|async)_(fifo|priority)", stem)
    if match:
        return {"executor": match.group(1), "scheduler": match.group(2)}
    return {"executor": stem, "scheduler": "unknown"}


def load_jsonl(path: str) -> list:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def flatten(record: dict, meta: dict) -> dict:
    os_m = record.get("os_metrics") or {}
    return {
        "experiment_id":        f"{meta['executor']}_{meta['scheduler']}",
        "executor":             meta["executor"],
        "scheduler":            meta["scheduler"],
        "job_id":               record.get("job_id"),
        "workload_type":        record.get("workload_type"),
        "priority":             record.get("priority"),
        "waiting_time":         record.get("waiting_time"),
        "execution_time":       record.get("execution_time"),
        "total_time":           record.get("total_time"),
        "error":                record.get("error"),
        "duration_s":           os_m.get("duration_s"),
        "cpu_user_delta_s":     os_m.get("cpu_user_delta_s"),
        "cpu_system_delta_s":   os_m.get("cpu_system_delta_s"),
        "ctx_voluntary_delta":  os_m.get("ctx_voluntary_delta"),
        "ctx_involuntary_delta":os_m.get("ctx_involuntary_delta"),
        "memory_mb":            os_m.get("memory_mb"),
        "memory_delta_mb":      os_m.get("memory_delta_mb"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", default="results")
    args = parser.parse_args()

    files = [
        os.path.join(args.results_dir, f)
        for f in os.listdir(args.results_dir)
        if f.endswith(".jsonl")
    ]

    if not files:
        print(f"No .jsonl files found in {args.results_dir}/")
        return

    rows = []
    for path in sorted(files):
        meta    = parse_meta(path)
        records = load_jsonl(path)
        for r in records:
            rows.append(flatten(r, meta))
        print(f"  {len(records):>4} records ← {os.path.basename(path)}")

    df  = pd.DataFrame(rows)
    out = os.path.join(args.results_dir, "summary.csv")
    df.to_csv(out, index=False)
    print(f"\nSummary → {out}  ({len(df)} total rows)")

    numeric = ["waiting_time", "execution_time", "total_time",
               "ctx_voluntary_delta", "ctx_involuntary_delta"]
    print("\n── Mean per experiment × workload ──────────────────────────────────")
    print(
        df.groupby(["executor", "scheduler", "workload_type"])[numeric]
        .mean().round(4).to_string()
    )


if __name__ == "__main__":
    main()
