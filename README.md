# IAM Policy Analysis Tool 🔐

This project provides a Python-based solution for analyzing AWS IAM policies and CloudTrail logs to generate **least privilege policy recommendations**.

---

## 📌 Project Features

- Compares IAM policies with actual CloudTrail usage logs.
- Identifies used, unused, and wildcard (*) actions.
- Generates least-privilege refined IAM policies in JSON form
- Removes unused and over-permissive permissions.
- Produces detailed CSV reports with reduction metrics.
- Supports MIT dataset, custom dataset, and combined dataset analysis.
- Automates all steps using run_all.py.
- Visualizes IAM usage with Amazon QuickSight.

---

## 🛠️ Tools & Technologies

- **AWS Services**: IAM, S3, CloudTrail, Lambda, Glue, Athena, QuickSight  
- **Languages/Libs**: Python (Boto3, JSON, Pandas)  
- **Tools**: VS Code, Git, GitHub

---

## 📁 Project Structure

iam-policy-analysis/
│
├── data/                         # CloudTrail event CSV files
│   ├── athena_event_counts.csv    # MIT dataset
│   ├── athena_events_custom.csv   # Custom dataset
│   ├── combined_events.csv        # Combined dataset
│   └── policy_usage_report.csv    # Generated usage reports
│
├── iam_policies/                  # Original IAM policies
│   ├── inline/                    # Inline IAM policies
│
├── refined_policies/              # Refined least-privilege policies
│   ├── mit/
│   ├── custom/
│   └── combined/
│
├── script/
│   ├── compare_policy_usage.py    # Compares policy with usage
│   ├── least_privilege_tool.py    # Generates refined policies
│   ├── combine_data.py            # Merges datasets
│   ├── fetch_iam_policies.py      # Fetches IAM managed policies
│   ├── fetch_inline_policies.py   # Fetches IAM inline policies
│   └── run_all.py                 # Automates full process
│
└── requirements.txt               # Python dependencies

---

## 📊 Output Files

- **Refined Policies**: Saved in refined_policies/<dataset>/ as JSON.
- **Summary Report**: policy_summary.csv showing action counts, wildcards, and % reduction.
- **Diff Files**: .diff files comparing original vs refined policies.

---

## 📄 License
This project is licensed under the MIT License.
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

### 1. Clone the Repository
```bash
git clone https://github.com/Devika258/iam-policy-analysis.git
cd iam-policy-analysis
---

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
---

### 3. Install Requirements
```bash
pip install -r requirements.txt
---

### 4. Run the analysis:
```bash
python least_privilege_tool.py

--------

## 📄 License
This project is licensed under the MIT License.
You can now:

1. Copy this into your `README.md` file.
2. Save it.
3. Commit and push:

```bash
git add README.md
git commit -m "Update README with full project details"
git push

---

## ✅  Running the Tool

### Run Full Automation for All Datasets
```bash
python script/run_all.py
---

### Run for Specific Dataset

### MIT Dataset:
```bash
python script/compare_policy_usage.py \
  --counts data/athena_event_counts.csv \
  --policies iam_policies \
  --inline iam_policies/inline \
  --output data/policy_usage_report_mit.csv

python script/least_privilege_tool.py \
  --usage data/policy_usage_report_mit.csv \
  --policies iam_policies/inline \
  --output refined_policies/mit
---

### Custom Dataset:
```bash
python script/compare_policy_usage.py \
  --counts data/athena_events_custom.csv \
  --policies iam_policies \
  --inline iam_policies/inline \
  --output data/policy_usage_report_custom.csv

python script/least_privilege_tool.py \
  --usage data/policy_usage_report_custom.csv \
  --policies iam_policies/inline \
  --output refined_policies/custom
---

### Combined Dataset:
```bash
python script/compare_policy_usage.py \
  --counts data/combined_events.csv \
  --policies iam_policies \
  --inline iam_policies/inline \
  --output data/policy_usage_report.csv

python script/least_privilege_tool.py \
  --usage data/policy_usage_report.csv \
  --policies iam_policies/inline \
  --output refined_policies/combined
---
