#!/usr/bin/env python3
import subprocess as sp
import sys
from pathlib import Path

# --- paths (adjust only if your folders differ)
ROOT = Path(__file__).resolve().parents[1]

COMPARE = ROOT / "script" / "compare_policy_usage.py"
LEAST   = ROOT / "script" / "least_privilege_tool.py"

# Inputs (these are exactly where your files are now)
MIT_COUNTS      = ROOT / "data" / "athena_event_counts.csv"
CUSTOM_COUNTS   = ROOT / "data" / "athena_events_custom.csv"
COMBINED_COUNTS = ROOT / "data" / "combined_events.csv"

# Policies
POLICIES_DIR = ROOT / "iam_policies"
INLINE_DIR   = POLICIES_DIR / "inline"

# Outputs
OUT_DIR          = ROOT / "data"
MIT_REPORT       = OUT_DIR / "policy_usage_report_mit.csv"
CUSTOM_REPORT    = OUT_DIR / "policy_usage_report_custom.csv"
COMBINED_REPORT  = OUT_DIR / "policy_usage_report.csv"  # keep your existing name

REFINED_DIR    = ROOT / "refined_policies"
REFINED_MIT    = REFINED_DIR / "mit"
REFINED_CUSTOM = REFINED_DIR / "custom"
REFINED_COMB   = REFINED_DIR / "combined"

def sh(args):
    print("\n$ " + " ".join(map(str, args)))
    cp = sp.run(args, cwd=ROOT)
    if cp.returncode != 0:
        sys.exit(cp.returncode)

def ensure_files():
    missing = [p for p in [COMPARE, LEAST, MIT_COUNTS, CUSTOM_COUNTS, COMBINED_COUNTS] if not p.exists()]
    if missing:
        print("❌ Missing required files:\n  " + "\n  ".join(map(str, missing)))
        sys.exit(1)
    for d in [REFINED_DIR, REFINED_MIT, REFINED_CUSTOM, REFINED_COMB]:
        d.mkdir(parents=True, exist_ok=True)

def run_compare(counts_path: Path, out_csv: Path):
    sh([
        sys.executable, str(COMPARE),
        "--counts", str(counts_path),
        "--policies", str(POLICIES_DIR),
        "--inline", str(INLINE_DIR),
        "--output", str(out_csv),
    ])
    print(f"✅ Usage report → {out_csv}")

def run_least_privilege(usage_csv: Path, output_dir: Path):
    sh([
        sys.executable, str(LEAST),
        "--usage", str(usage_csv),
        "--policies", str(INLINE_DIR),
        "--output", str(output_dir),
    ])
    print(f"✨ Refined policies written to → {output_dir}")

def main():
    ensure_files()

    print("\n================ 1) MIT =================")
    run_compare(MIT_COUNTS, MIT_REPORT)
    run_least_privilege(MIT_REPORT, REFINED_MIT)

    print("\n================ 2) CUSTOM ==============")
    run_compare(CUSTOM_COUNTS, CUSTOM_REPORT)
    run_least_privilege(CUSTOM_REPORT, REFINED_CUSTOM)

    print("\n================ 3) COMBINED ============")
    run_compare(COMBINED_COUNTS, COMBINED_REPORT)
    run_least_privilege(COMBINED_REPORT, REFINED_COMB)

    print("\n✅ All done!")
    print(f"- MIT report:         {MIT_REPORT}")
    print(f"- Custom report:      {CUSTOM_REPORT}")
    print(f"- Combined report:    {COMBINED_REPORT}")
    print(f"- Refined (MIT):      {REFINED_MIT}")
    print(f"- Refined (Custom):   {REFINED_CUSTOM}")
    print(f"- Refined (Combined): {REFINED_COMB}")

if __name__ == "__main__":
    main()
