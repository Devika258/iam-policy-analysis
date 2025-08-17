# IAM Policy Analysis Tool

This project provides a Python-based solution for analyzing AWS IAM policies and CloudTrail logs to generate **least privilege policy recommendations**.

---

## Project Features

- **Policy-Usage Comparison** – Matches IAM policies against CloudTrail logs.
- **Least Privilege Refinement** – Identifies used, unused, and wildcard (*) actions.
- **Automatic Reduction** – Removes unnecessary permissions to minimize risk.
- **Detailed Reports** – Generates CSV summaries with action counts, risk scores, and % reductions.
- **Refined Policies** – Outputs new JSON policies optimized for least privilege.
- **Multiple Datasets** – Supports MIT dataset, custom dataset, and combined dataset.
- **Automation** – run_all.py executes the entire pipeline in one ste
- **Visualization** – Integrates with Amazon QuickSight for interactive dashboards.

---

## Tools & Technologies

- **AWS Services**: IAM, S3, CloudTrail, Lambda, Glue, Athena, QuickSight  
- **Languages/Libs**: Python (Boto3, JSON, Pandas)  
- **Tools**: VS Code, Git, GitHub

---

## Project Structure
```bash

iam-policy-analysis/
│
├── data/                         # CloudTrail event CSV files
│   ├── athena_event_counts.csv    # MIT dataset
│   ├── athena_events_custom.csv   # Custom dataset
│   ├── combined_events.csv        # Combined dataset
│   ├── policy_usage_report.csv    # Combined usage report
│   ├── policy_usage_report_mit.csv# MIT usage report
│   ├── policy_usage_report_custom.csv # Custom usage report
│   └── policy_usage_report_mid.csv    # Mid usage report
│
├── iam_policies/                  # Original IAM policies
│   ├── inline/                    # Inline IAM policies
│
├── refined_policies/              # Refined least-privilege policies
│   ├── mit/                       # MIT dataset refined policies
│   ├── custom/                    # Custom dataset refined policies
│   ├── combined/                  # Combined dataset refined policies
│   ├── new/                       # New dataset refined policies
│   └── mid60/                     # Mid60 dataset refined policies
│
├── script/                        # Automation and analysis scripts
│   ├── compare_policy_usage.py    # Compares policy with usage
│   ├── least_privilege_tool.py    # Generates refined policies
│   ├── combine_data.py            # Merges datasets
│   ├── fetch_iam_policies.py      # Fetches IAM managed policies
│   ├── fetch_inline_policies.py   # Fetches IAM inline policies
│   ├── fix_policy_summary.py      # (new) Fix/clean summary reports
│   └── run_all.py                 # Automates full process
│
├── test_refined_mit/              # Test refined output (MIT dataset)
├── test_refined_custom/           # Test refined output (Custom dataset)
├── test_refined_new/              # Test refined output (New dataset)
├── test_refined_mid60/            # Test refined output (Mid60 dataset)
│
├── requirements.txt               # Python dependencies
├── LICENSE
└── README.md

```
---

## Output Files

- **Refined Policies**: Saved in refined_policies/<dataset>/ as JSON.
- **Summary Report**: policy_summary.csv showing action counts, wildcards, and % reduction.
- **Diff Files**: .diff files comparing original vs refined policies.

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Devika258/iam-policy-analysis.git
cd iam-policy-analysis
```
---

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```
---

### 3. Install Requirements
```bash
pip install -r requirements.txt
```
---

### 4. Run the analysis:
```bash
python least_privilege_tool.py
```
--------

## A. Running the Tool

### Run Full Automation for All Datasets
```bash
python script/run_all.py
```
---

### B. Run for Specific Dataset

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
```
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
```
---

### New Dataset:
```bash
python script/compare_policy_usage.py \
  --counts data/athena_events_new.csv \
  --policies iam_policies \
  --inline iam_policies/inline \
  --output data/policy_usage_report_new.csv

python script/least_privilege_tool.py \
  --usage data/policy_usage_report_new.csv \
  --policies iam_policies/inline \
  --output refined_policies/new
```
---

### Mid Dataset:
```bash
python script/compare_policy_usage.py \
  --counts data/athena_events_mid60.csv \
  --policies iam_policies \
  --inline iam_policies/inline \
  --output data/policy_usage_report_mid60.csv

python script/least_privilege_tool.py \
  --usage data/policy_usage_report_mid60.csv \
  --policies iam_policies/inline \
  --output refined_policies/mid60
```
---

## License
This project is licensed under the MIT License.

---
