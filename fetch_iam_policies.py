import boto3
import json
import os

# Step 1: Setup IAM client
iam = boto3.client('iam')

# Step 2: Create output folder
output_dir = 'iam_policies'
os.makedirs(output_dir, exist_ok=True)

# Step 3: Fetch and save customer-managed IAM policies
def fetch_and_save_policies():
    print("🔍 Fetching policies...")
    response = iam.list_policies(Scope='Local', MaxItems=1000)

    for policy in response['Policies']:
        policy_name = policy['PolicyName']
        policy_arn = policy['Arn']
        default_version_id = policy['DefaultVersionId']

        # Fetch actual policy document
        version = iam.get_policy_version(
            PolicyArn=policy_arn,
            VersionId=default_version_id
        )

        document = version['PolicyVersion']['Document']

        # Save policy to JSON file
        file_path = os.path.join(output_dir, f"{policy_name}.json")
        with open(file_path, 'w') as f:
            json.dump(document, f, indent=2)

        print(f"✅ Saved policy: {policy_name}")

# Step 4: Run the function
if __name__ == "__main__":
    fetch_and_save_policies()
