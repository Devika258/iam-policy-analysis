import os
import json
import pandas as pd
import argparse

def load_usage_report(report_path):
    df = pd.read_csv(report_path)
    usage_map = {}
    for _, row in df.iterrows():
        policy = row['Policy File']
        action = row['Action']
        status = row['Status'].strip().lower()

        if status == 'used':
            usage_map.setdefault(policy, []).append(action)
    return usage_map

def process_policy(policy_path, used_actions):
    with open(policy_path, 'r') as f:
        policy_json = json.load(f)

    refined_statements = []
    flagged_wildcards = []

    for stmt in policy_json.get("Statement", []):
        if stmt['Effect'] != 'Allow':
            continue

        original_actions = stmt.get('Action', [])
        if isinstance(original_actions, str):
            original_actions = [original_actions]

        filtered = []
        for act in original_actions:
            if act in used_actions:
                filtered.append(act)
            elif '*' in act:
                flagged_wildcards.append(act)

        if filtered:
            refined_statements.append({
                "Effect": "Allow",
                "Action": filtered,
                "Resource": stmt.get("Resource", "*")
            })

    return {
        "Version": policy_json.get("Version", "2012-10-17"),
        "Statement": refined_statements
    }, flagged_wildcards

def write_summary(summary_list, output_path):
    df = pd.DataFrame(summary_list)
    df.to_csv(output_path, index=False)
    print(f"✅ Summary written to: {output_path}")

def main(args):
    usage_map = load_usage_report(args.usage)
    summary = []

    for filename in os.listdir(args.policies):
        if not filename.endswith('.json'):
            continue

        full_path = os.path.join(args.policies, filename)
        used = usage_map.get(filename, [])
        refined_policy, wildcards = process_policy(full_path, used)

        output_file = filename.replace(".json", "_refined.json")
        out_path = os.path.join(args.output, output_file)
        with open(out_path, 'w') as f:
            json.dump(refined_policy, f, indent=2)

        total = len(used) + len(wildcards)
        reduction = 0
        if total > 0:
            reduction = round(((total - len(used)) / total) * 100, 2)

        summary.append({
            "Policy": filename,
            "Total Actions": total,
            "Used": len(used),
            "Wildcards Flagged": len(wildcards),
            "% Reduction": f"{reduction}%"
        })

        print(f"✔ Processed {filename} → {output_file}")
        if wildcards:
            print(f"⚠️ Wildcards found in {filename}: {wildcards}")

    write_summary(summary, os.path.join(args.output, "policy_summary.csv"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate least privilege IAM policies.")
    parser.add_argument("--policies", required=True, help="Folder with IAM policy JSON files")
    parser.add_argument("--usage", required=True, help="CSV file with policy usage report")
    parser.add_argument("--output", required=True, help="Folder to write refined policies and summary")
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    main(args)
