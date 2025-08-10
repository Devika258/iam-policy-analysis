import os
import json
import csv
import argparse
from typing import Dict, Iterable, List, Set, Tuple

# ---------- Helpers ----------

def load_used_actions_from_csv(csv_file: str) -> Set[str]:
    """
    Load CloudTrail event names from a CSV (robust header detection).
    Works with headers like: eventname, eventName, event_name.
    If a 'dataset,eventname' CSV is passed, it will pick 'eventname'.
    Falls back to a sensible column if needed.
    Returns a LOWERCASED set of event names (e.g., 'putobject').
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Counts file not found: {csv_file}")

    used: Set[str] = set()
    with open(csv_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"No header row found in CSV: {csv_file}")

        original_headers = reader.fieldnames
        lower_to_orig = {h.lower(): h for h in original_headers}

        key = None
        # 1) Preferred headers
        if "eventname" in lower_to_orig:
            key = lower_to_orig["eventname"]
        elif "event_name" in lower_to_orig:
            key = lower_to_orig["event_name"]
        elif "eventName" in original_headers:  # exact camel-case check
            key = "eventName"

        # 2) Fallbacks if event name not explicit
        if key is None:
            # Common combined CSV: ['dataset', 'eventname']
            if original_headers[0].lower() == "dataset" and len(original_headers) > 1:
                key = original_headers[1]
            else:
                # Last resort: use the first column
                key = original_headers[0]

        for row in reader:
            val = (row.get(key) or "").strip()
            if val:
                used.add(val.lower())

    return used


def extract_actions(policy_json: Dict) -> Set[str]:
    """
    Extract all actions from a policy JSON (handles string or list).
    Returns the raw 'service:Action' strings.
    """
    actions: Set[str] = set()
    stmts = policy_json.get("Statement", [])
    if not isinstance(stmts, list):
        stmts = [stmts]

    for stmt in stmts:
        action = stmt.get("Action", [])
        if isinstance(action, str):
            actions.add(action)
        elif isinstance(action, list):
            for a in action:
                if isinstance(a, str):
                    actions.add(a)
    return actions


def compare_policy_to_usage(policy_path: str, used_events_lower: Set[str]) -> List[Tuple[str, str]]:
    """
    Compare a single policy to used CloudTrail events.
    Returns list of tuples: (action, 'Used'|'Unused'|'Wildcard').
    """
    with open(policy_path, "r", encoding="utf-8") as f:
        policy = json.load(f)

    actions = extract_actions(policy)
    findings: List[Tuple[str, str]] = []

    print(f"\n📄 Policy: {os.path.basename(policy_path)}")
    for action in sorted(actions):
        # Wildcards like 's3:*'
        if "*" in action:
            print(f"  ⚠️  Wildcard Action: {action}")
            findings.append((action, "Wildcard"))
            continue

        # Compare suffix (after 'service:') case-insensitively to CloudTrail event names
        suffix = action.split(":", 1)[-1].lower()
        if suffix in used_events_lower:
            print(f"  ✅ Used:   {action}")
            findings.append((action, "Used"))
        else:
            print(f"  ❌ Unused: {action}")
            findings.append((action, "Unused"))

    return findings


def write_report_to_csv(results: Dict[str, Iterable[Tuple[str, str]]], output_file: str) -> None:
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Policy File", "Action", "Status"])
        for policy_file, rows in results.items():
            for action, status in rows:
                writer.writerow([policy_file, action, status])
    print(f"\n📄 Report saved to: {output_file}")


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser(
        description="Compare IAM policy actions against CloudTrail event usage."
    )
    parser.add_argument(
        "--counts",
        default="data/athena_event_counts.csv",
        help="Path to CSV containing CloudTrail event names "
             "(e.g., data/athena_event_counts.csv, data/athena_events_custom.csv, or data/combined_events.csv)",
    )
    parser.add_argument(
        "--policies",
        default="iam_policies",
        help="Directory containing managed policies (default: iam_policies)",
    )
    parser.add_argument(
        "--inline",
        default=None,
        help="Directory containing inline policies (default: <policies>/inline)",
    )
    parser.add_argument(
        "--output",
        default="data/policy_usage_report.csv",
        help="Output CSV path (default: data/policy_usage_report.csv)",
    )
    args = parser.parse_args()

    policies_dir = args.policies
    inline_dir = args.inline or os.path.join(policies_dir, "inline")

    print("Loading CloudTrail event usage …")
    used_events_lower = load_used_actions_from_csv(args.counts)
    print(f"Loaded {len(used_events_lower)} unique event names from: {args.counts}")
    # Show a tiny sample so you can sanity‑check quickly
    try:
        preview = ", ".join(sorted(list(used_events_lower))[:8])
        print(f"Sample events: {preview} …")
    except Exception:
        pass

    results: Dict[str, List[Tuple[str, str]]] = {}

    # Managed policies (top-level JSON files under iam_policies/)
    if os.path.isdir(policies_dir):
        for file in sorted(os.listdir(policies_dir)):
            if file.endswith(".json"):
                path = os.path.join(policies_dir, file)
                policy_findings = compare_policy_to_usage(path, used_events_lower)
                results[file] = policy_findings

    # Inline policies (JSON files under iam_policies/inline/)
    if os.path.isdir(inline_dir):
        for file in sorted(os.listdir(inline_dir)):
            if file.endswith(".json"):
                path = os.path.join(inline_dir, file)
                policy_findings = compare_policy_to_usage(path, used_events_lower)
                results[file] = policy_findings

    write_report_to_csv(results, args.output)


if __name__ == "__main__":
    main()

