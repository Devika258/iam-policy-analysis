import os
import json
import pandas as pd

# Paths
raw_policies_dir = 'iam_policies/'          # Input folder
report_file = 'policy_usage_report.csv'     # Usage report
output_dir = 'refined_policies/'            # Output folder

# Create output directory if needed
os.makedirs(output_dir, exist_ok=True)

# Load the report
usage_df = pd.read_csv(report_file)

# Group actions by policy
policy_usage_map = {}
for _, row in usage_df.iterrows():
    policy = row['Policy File'].replace('.json', '')  # Strip .json if needed
    action = row['Action']
    status = row['Status']
    
    if status.strip() == 'Used' or status.strip() == '✅':
        policy_usage_map.setdefault(policy, []).append(action)

# Iterate through each policy file
for policy_file in os.listdir(raw_policies_dir):
    if not policy_file.endswith('.json'):
        continue

    policy_path = os.path.join(raw_policies_dir, policy_file)
    with open(policy_path, 'r') as f:
        policy_json = json.load(f)

    policy_name = os.path.splitext(policy_file)[0]  # Remove .json
    used_actions = policy_usage_map.get(policy_name, [])

    refined_statements = []

    # Rebuild policy with only used actions
    for stmt in policy_json.get('Statement', []):
        if stmt['Effect'] != 'Allow':
            continue

        original_actions = stmt.get('Action', [])
        if isinstance(original_actions, str):
            original_actions = [original_actions]

        filtered_actions = [a for a in original_actions if a in used_actions]

        if filtered_actions:
            new_stmt = {
                "Effect": "Allow",
                "Action": filtered_actions,
                "Resource": stmt.get('Resource', '*')
            }
            refined_statements.append(new_stmt)

    # Final policy output
    refined_policy = {
        "Version": policy_json.get("Version", "2012-10-17"),
        "Statement": refined_statements
    }

    output_path = os.path.join(output_dir, f'{policy_name}_refined.json')
    with open(output_path, 'w') as f:
        json.dump(refined_policy, f, indent=2)

    print(f"✔ Refined policy written: {output_path}")
