import os
import json
import argparse
from typing import List, Dict, Tuple
import pandas as pd

# --------------------------
# Load "used" actions per policy from the usage CSV
# --------------------------
def load_usage_report(report_path: str) -> Dict[str, List[str]]:
    """
    Returns: { 'PolicyFile.json': ['service:action', ... lowercased] }
    Only actions with Status == 'Used' are included.
    """
    df = pd.read_csv(report_path)
    usage_map: Dict[str, List[str]] = {}
    for _, row in df.iterrows():
        policy = str(row['Policy File']).strip()
        action = str(row['Action']).strip().lower()
        status = str(row['Status']).strip().lower()
        if status == 'used':
            usage_map.setdefault(policy, []).append(action)
    return usage_map

# --------------------------
# Extract actions from a policy JSON
# --------------------------
def flatten_actions(stmt_actions) -> List[str]:
    if stmt_actions is None:
        return []
    if isinstance(stmt_actions, str):
        return [stmt_actions]
    if isinstance(stmt_actions, list):
        return [a for a in stmt_actions if isinstance(a, str)]
    return []

def collect_original_actions(policy_json: Dict) -> List[str]:
    actions: List[str] = []
    statements = policy_json.get("Statement", [])
    if not isinstance(statements, list):
        statements = [statements]
    for stmt in statements:
        if stmt.get("Effect") != "Allow":
            continue
        actions.extend(flatten_actions(stmt.get("Action")))
    return actions

# --------------------------
# Build refined policy & metrics
# --------------------------
def process_policy(policy_path: str, used_actions_lower: List[str]) -> Tuple[Dict, Dict, str]:
    """
    Returns:
      refined_policy_json,
      metrics dict,
      human-readable diff string
    """
    with open(policy_path, "r", encoding="utf-8") as f:
        policy = json.load(f)

    original_actions = collect_original_actions(policy)
    original_count = len(original_actions)

    # Classify actions
    used_set_lower = set(a.lower() for a in used_actions_lower)
    kept_actions: List[str] = []
    wildcard_actions: List[str] = []
    unused_actions: List[str] = []

    for act in original_actions:
        if '*' in act:
            wildcard_actions.append(act)
            # Do not keep wildcards in refined policy
        elif act.lower() in used_set_lower:
            kept_actions.append(act)
        else:
            unused_actions.append(act)

    # Build refined policy with only the kept actions
    refined_statements = []
    if kept_actions:
        refined_statements.append({
            "Effect": "Allow",
            "Action": sorted(kept_actions),
            "Resource": "*"  # keep original resource if you prefer; this is simplest
        })

    refined = {
        "Version": policy.get("Version", "2012-10-17"),
        "Statement": refined_statements
    }

    # Metrics
    kept_count = len(kept_actions)
    wildcard_count = len(wildcard_actions)
    unused_count = len(unused_actions)
    reduction = 0.0
    if original_count > 0:
        reduction = round((original_count - kept_count) * 100.0 / original_count, 2)

    metrics = {
        "Original Actions": original_count,
        "Kept (Used)": kept_count,
        "Unused (Removed)": unused_count,
        "Wildcards Flagged": wildcard_count,
        "% Reduction vs Original": f"{reduction}%"
    }

    # Diff
    diff_lines = [
        f"- Original total actions: {original_count}",
        f"  · kept(used): {kept_count}",
        f"  · unused:     {unused_count}",
        f"  · wildcards:  {wildcard_count}",
        "",
        "Original actions:",
        *([f"  - {a}" for a in original_actions] if original_actions else ["  (none)"]),
        "",
        "Kept (used) actions:",
        *([f"  + {a}" for a in kept_actions] if kept_actions else ["  (none)"]),
        "",
        "Wildcard actions (removed):",
        *([f"  ! {a}" for a in wildcard_actions] if wildcard_actions else ["  (none)"]),
    ]

    return refined, metrics, "\n".join(diff_lines)

# --------------------------
# Write helpers
# --------------------------
def write_json(path: str, data: Dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def write_text(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def write_summary(rows: List[Dict], out_csv: str):
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"✅ Summary written to: {out_csv}")

# --------------------------
# CLI
# --------------------------
def main():
    ap = argparse.ArgumentParser(description="Generate least-privilege versions of IAM policies based on usage.")
    ap.add_argument("--policies", required=True, help="Folder containing policy JSON files to refine")
    ap.add_argument("--usage", required=True, help="CSV produced by compare_policy_usage.py")
    ap.add_argument("--output", required=True, help="Folder to write refined policies and reports")
    args = ap.parse_args()

    os.makedirs(args.output, exist_ok=True)
    usage_map = load_usage_report(args.usage)

    summary_rows: List[Dict] = []

    for fname in sorted(os.listdir(args.policies)):
        if not fname.endswith(".json"):
            continue
        policy_path = os.path.join(args.policies, fname)
        used_actions = usage_map.get(fname, [])

        refined_json, metrics, diff_str = process_policy(policy_path, used_actions)

        # outputs
        base = fname[:-5]  # strip .json
        refined_path = os.path.join(args.output, f"{base}_refined.json")
        diff_path = os.path.join(args.output, f"{base}_refined.diff")

        write_json(refined_path, refined_json)
        write_text(diff_path, diff_str)

        print(f"✔ Processed {fname} → {os.path.basename(refined_path)}")
        print(f"  ↳ Diff: {os.path.basename(diff_path)}")

        # add summary row
        summary_rows.append({
            "Policy": fname,
            **metrics
        })

    write_summary(summary_rows, os.path.join(args.output, "policy_summary.csv"))

if __name__ == "__main__":
    main()
