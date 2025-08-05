# IAM Policy Analysis Tool 🔐

This project provides a Python-based solution for analyzing AWS IAM policies and CloudTrail logs to generate **least privilege policy recommendations**.

---

## 📌 Project Features

- Parses and reformats AWS CloudTrail logs into NDJSON format.
- Extracts actual IAM usage data via Athena.
- Compares current IAM policies with actual usage.
- Flags unused, wildcard, or over-permissive actions.
- Generates refined IAM policies in JSON.
- Produces summary CSV reports.
- Visualizes IAM usage with Amazon QuickSight.

---

## 🛠️ Tools & Technologies

- **AWS Services**: IAM, S3, CloudTrail, Lambda, Glue, Athena, QuickSight  
- **Languages/Libs**: Python (Boto3, JSON, Pandas)  
- **Tools**: VS Code, Git, GitHub

---

## 📊 Example Output

- ✅ Used permissions  
- ❌ Unused permissions  
- ⚠️ Wildcard actions (e.g., `s3:*`, `iam:*`)  
- 📉 Reduction summary: `policy_summary.csv`  
- 📊 Visual dashboard: QuickSight charts  

---

## 📁 Project Structure

├── iam_policies/                # Original IAM policies
├── refined_policies/            # Optimized policies after analysis
├── policy_usage_report.csv      # IAM action usage report
├── policy_summary.csv           # Policy reduction summary
├── fetch_iam_policies.py        # Script to fetch managed IAM policies
├── fetch_inline_policies.py     # Script to fetch inline policies
├── compare_policy_usage.py      # Policy usage comparison tool
├── least_privilege_tool.py      # Refines IAM policies based on usage
└── generate_refined_policies.py # (Optional) Wrapper script

---

## 📄 License


You can now:

1. Copy this into your `README.md` file.
2. Save it.
3. Commit and push:

```bash
git add README.md
git commit -m "Update README with full project details"
git push

---


## ✅ Getting Started

### Clone the repo:
```bash
git clone https://github.com/Devika258/iam-policy-analysis.git
cd iam-policy-analysis
---

### Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
---

### Install requirements:
```bash
pip install -r requirements.txt
---

### Run the analysis:
```bash
python least_privilege_tool.py


