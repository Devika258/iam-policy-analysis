#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
import pandas as pd

def lpr_recommendation(keep_pct: float, high_min: float, med_min: float) -> str:
    # High if >= high_min, Medium if [med_min, high_min), Low otherwise.
    if keep_pct >= high_min:
        return "High: This policy is already highly optimized for least privilege."
    elif med_min <= keep_pct < high_min:
        return "Medium: This policy could be improved by removing some unused permissions."
    else:
        return "Low: This policy is over-provisioned and needs significant trimming."

def recalc(df: pd.DataFrame, exclude_wildcards: bool, high_min: float, med_min: float) -> pd.DataFrame:
    # Normalize expected column names (exact names used by your tool)
    must_have = ["Original Actions", "Kept (Used)"]
    for name in must_have:
        if name not in df.columns:
            raise ValueError(f"Missing required column: {name}")

    # Optional column
    wildcards = df["Wildcards Flagged"] if "Wildcards Flagged" in df.columns else 0

    # Denominator
    if exclude_wildcards:
        denom = (df["Original Actions"] - (wildcards if isinstance(wildcards, pd.Series) else 0)).clip(lower=0)
    else:
        denom = df["Original Actions"].clip(lower=0)

    # Keep% (Least-Privilege %) and Reduction%
    keep_pct = (df["Kept (Used)"] * 100.0 / denom.where(denom > 0, other=1)).round(2)
    keep_pct = keep_pct.where(denom > 0, other=0.0)
    reduction_pct = (100.0 - keep_pct).round(2)

    # Write back
    df["Least-Privilege %"] = keep_pct
    df["pct_reduction_num"] = reduction_pct
    df["% Reduction vs Original"] = df["pct_reduction_num"].map(lambda x: f"{x}%")

    # Recommendation string (based on KEEP %, not reduction)
    df["Least privilage recommendation"] = keep_pct.map(lambda v: lpr_recommendation(v, high_min, med_min))
    return df

def main():
    ap = argparse.ArgumentParser(description="Recalculate Least-Privilege % in policy_summary.csv files.")
    ap.add_argument("paths", nargs="+", help="Folders that contain policy_summary.csv (e.g. refined_policies/mit test_refined_custom)")
    ap.add_argument("--exclude-wildcards", action="store_true",
                    help="Exclude Wildcards Flagged from the denominator when computing the percentage.")
    ap.add_argument("--high-min", type=float, default=90.0,
                    help="Minimum keep%% to be considered High (default: 90)")
    ap.add_argument("--med-min", type=float, default=40.0,
                    help="Minimum keep%% to be considered Medium (default: 40)")
    args = ap.parse_args()

    any_done = False
    for p in args.paths:
        folder = Path(p)
        csv_path = folder / "policy_summary.csv"
        if not csv_path.exists():
            print(f"Skipping {folder}: no policy_summary.csv")
            continue

        print(f"\nFixing {csv_path}  (exclude_wildcards={args.exclude_wildcards}, High>={args.high_min}, Medium>={args.med_min})")
        df = pd.read_csv(csv_path)
        df2 = recalc(df, args.exclude_wildcards, args.high_min, args.med_min)
        df2.to_csv(csv_path, index=False)
        print(f"✅ Updated: {csv_path}  (rows: {len(df2)})")
        any_done = True

    if not any_done:
        print("No files updated. Provide folder(s) that contain policy_summary.csv.")
        sys.exit(2)

if __name__ == "__main__":
    main()
