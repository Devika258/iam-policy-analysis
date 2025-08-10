import boto3
import json
import os

iam = boto3.client('iam')
output_dir = 'iam_policies/inline'
os.makedirs(output_dir, exist_ok=True)

def save_inline_policy(entity_type, entity_name, policy_name, document):
    filename = f"{entity_type}_{entity_name}_{policy_name}.json"
    path = os.path.join(output_dir, filename)
    with open(path, 'w') as f:
        json.dump(document, f, indent=2)
    print(f"✅ Saved {entity_type} policy: {filename}")

def fetch_inline_user_policies():
    users = iam.list_users()['Users']
    for user in users:
        user_name = user['UserName']
        policies = iam.list_user_policies(UserName=user_name)['PolicyNames']
        for policy_name in policies:
            policy = iam.get_user_policy(UserName=user_name, PolicyName=policy_name)
            save_inline_policy('user', user_name, policy_name, policy['PolicyDocument'])

def fetch_inline_role_policies():
    roles = iam.list_roles()['Roles']
    for role in roles:
        role_name = role['RoleName']
        policies = iam.list_role_policies(RoleName=role_name)['PolicyNames']
        for policy_name in policies:
            policy = iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
            save_inline_policy('role', role_name, policy_name, policy['PolicyDocument'])

def fetch_inline_group_policies():
    groups = iam.list_groups()['Groups']
    for group in groups:
        group_name = group['GroupName']
        policies = iam.list_group_policies(GroupName=group_name)['PolicyNames']
        for policy_name in policies:
            policy = iam.get_group_policy(GroupName=group_name, PolicyName=policy_name)
            save_inline_policy('group', group_name, policy_name, policy['PolicyDocument'])

if __name__ == "__main__":
    print("🔍 Fetching inline policies...")
    fetch_inline_user_policies()
    fetch_inline_role_policies()
    fetch_inline_group_policies()
    print("🎉 All inline policies retrieved.")
