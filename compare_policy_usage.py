import os
import json
import csv

# === CONFIGURATION ===
policy_dir = 'iam_policies'
inline_dir = os.path.join(policy_dir, 'inline')
cloudtrail_csv = '282da5e6-bc46-4185-a5f1-23e58a1c2236.csv'
output_file = 'policy_usage_report.csv'

# === Step 1: Load eventNames from CloudTrail CSV ===
def load_used_actions_from_csv(csv_file):
    used_actions = set()
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            used_actions.add(row['eventname'])  # Adjust this if header changes
    return used_actions

# === Step 2: Extract actions from IAM policy ===
def extract_actions(policy_json):
    actions = set()
    statements = policy_json.get('Statement', [])
    if not isinstance(statements, list):
        statements = [statements]
    for stmt in statements:
        action = stmt.get('Action', [])
        if isinstance(action, str):
            actions.add(action)
        elif isinstance(action, list):
            actions.update(action)
    return actions

# === Step 3: Compare each action to used CloudTrail events ===
def compare_policy_to_usage(policy_path, used_actions):
    with open(policy_path) as f:
        policy = json.load(f)

    policy_actions = extract_actions(policy)
    findings = []

    print(f"\n📄 Policy: {os.path.basename(policy_path)}")
    for action in policy_actions:
        if '*' in action:
            print(f"  ⚠️ Wildcard Action: {action}")
            findings.append((action, 'Wildcard'))
        elif action.split(':')[-1] in used_actions:
            print(f"  ✅ Used: {action}")
            findings.append((action, 'Used'))
        else:
            print(f"  ❌ Unused: {action}")
            findings.append((action, 'Unused'))

    return findings

# === Step 4: Export results to CSV ===
def write_report_to_csv(results):
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Policy File', 'Action', 'Status'])
        for policy_file, data in results.items():
            for action, status in data:
                writer.writerow([policy_file, action, status])
    print(f"\n📄 Report saved to: {output_file}")

# === MAIN RUNNER ===
def run_comparison():
    used_actions = load_used_actions_from_csv(cloudtrail_csv)
    results = {}

    # Managed policies
    for file in os.listdir(policy_dir):
        if file.endswith('.json'):
            path = os.path.join(policy_dir, file)
            results[file] = compare_policy_to_usage(path, used_actions)

    # Inline policies
    for file in os.listdir(inline_dir):
        if file.endswith('.json'):
            path = os.path.join(inline_dir, file)
            results[file] = compare_policy_to_usage(path, used_actions)

    write_report_to_csv(results)

if __name__ == "__main__":
    run_comparison()
