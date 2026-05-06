# Portugal Term Deposit Comparator

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![pandas](https://img.shields.io/badge/pandas-Data%20Analysis-blue)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-purple)
![Data Governance](https://img.shields.io/badge/Data%20Governance-Human%20Validation-green)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

🔗 **Live App:** https://pt-deposit-comparator.streamlit.app

A Python/Streamlit tool to compare Portuguese term deposits by estimated net yield, maturity, eligibility criteria and liquidity conditions.

This project was created as a practical banking and data analysis mini-project, combining financial product analysis, Python, pandas, Streamlit, Plotly, official source monitoring and a human-in-the-loop validation workflow.

Beyond the simulator itself, this project includes a validation workflow for official bank sources and FIN/PDF documents, making it closer to a real banking data governance and product monitoring process.

---

## Project Overview

The goal of this project is to compare term deposit products available in Portugal and estimate the net return for different maturities and investment amounts.

The tool allows users to filter deposits based on:

- Investment amount
- Maturity
- Bank
- New client eligibility
- New money requirements
- Early withdrawal conditions
- Estimated withholding tax

The output ranks eligible deposits by estimated net interest.

The project is designed not only as a simulator, but also as a practical example of banking product analysis, financial calculation logic, data validation and controlled dataset governance.

---

## Market Scope

The dataset focuses on:

- Portuguese banks
- Banks with physical or established presence in Portugal
- Selected online banks relevant to Portuguese residents

The dataset is manually curated and should always be validated against official bank documentation before any financial decision.

---

## Current Features

- Compare Portuguese term deposit products by estimated net return
- Simulate gross interest, withholding tax, net interest and estimated final amount
- Filter deposits by:
  - Investment amount
  - Maturity
  - Bank
  - New client eligibility
  - New money requirements
  - Early withdrawal availability
- Simple and Advanced app modes
- Ranking table sorted by estimated net interest
- Interactive Plotly chart for net interest comparison
- Product details, notes and official source references
- CSV and Excel export of ranking results
- Human-in-the-loop validation workflow
- Official source monitoring through snapshot comparison
- FIN/PDF validation reader for official bank product documents
- Banco BiG-specific FIN/PDF parsing support
- Manual review workflow before dataset updates
- Approved update workflow for controlled dataset changes
- Data quality and validation transparency inside the Streamlit app

---

## Validation Workflow

This project includes a human-in-the-loop validation workflow designed to make financial product data updates more controlled and transparent.

The validation process includes:

1. Monitoring official bank product sources
2. Comparing source snapshots against the previous baseline
3. Flagging changed or unavailable sources
4. Reviewing official product pages and FIN/PDF documents
5. Recording a human validation decision
6. Updating the dataset only after manual approval

The project also includes a FIN/PDF reader that extracts key fields from official bank documents when possible, including:

- Bank
- Product
- Maturity
- TANB
- Minimum amount
- Maximum amount
- Early withdrawal conditions
- Renewal conditions
- Access conditions
- Document validity

Some PDF documents may require manual confirmation due to formatting limitations. In those cases, the system explicitly flags the item for human review instead of applying automatic updates.

---

## Data Quality & Human Validation

The app uses a manually curated dataset and does not automatically update deposit rates or product conditions without human review.

Validation controls include:

- Dataset reference date
- Last manual validation date
- Official source tracking
- Local validation reports
- Snapshot baseline monitoring
- FIN/PDF review workflow
- Human validation notes

This approach reflects a conservative data governance process where source changes can be detected, but dataset updates require manual validation.

---

## Methodology

For each eligible deposit, the app estimates:

Gross interest = Capital × TANB × Maturity / 12  
Withholding tax = Gross interest × Tax rate  
Net interest = Gross interest - Withholding tax  
Estimated final amount = Capital + Net interest

The default withholding tax assumption is based on a 28% Portuguese tax rate for interest income.

The calculations are simplified estimates and may not reflect all possible fees, tax situations, account costs, exemptions or special product conditions.

---

## Repository Structure

portugal-term-deposit-comparator/
│
├── app.py
├── README.md
├── requirements.txt
├── LICENSE
│
├── data/
│   └── depositos_prazo_core_portugal_corrigido.csv
│
├── scripts/
│   ├── monitor_sources.py
│   ├── validation_summary.py
│   ├── generate_grouped_review.py
│   ├── propose_dataset_updates.py
│   ├── apply_approved_updates.py
│   └── read_fin_pdf.py
│
├── validation/
│   ├── latest_validation_summary.csv
│   ├── review_required.csv
│   ├── fin_pdf_review.md
│   └── validation_report_*.csv
│
├── snapshots/
│   └── source_snapshots.json
│
├── incoming_fin/
│   └── .gitkeep
│
├── examples/
│   ├── export_ranking.py
│   └── export_ranking_excel.py
│
├── outputs/
│   └── exported ranking files
│
└── notebooks/
    └── optional analysis notebooks

Uploaded FIN/PDF files are processed locally through the `incoming_fin/` folder and are intentionally excluded from the repository through `.gitignore`.

---

## How to Run Locally

Clone the repository:

git clone https://github.com/ricardoserodio/portugal-term-deposit-comparator.git  
cd portugal-term-deposit-comparator

Install dependencies:

pip install -r requirements.txt

Run the Streamlit app:

streamlit run app.py

---

## Source Monitoring Workflow

Run source monitoring:

python scripts/monitor_sources.py

Generate validation summary:

python scripts/validation_summary.py

Generate grouped review:

python scripts/generate_grouped_review.py

Accept validated source snapshots:

python scripts/monitor_sources.py --accept-snapshots

---

## FIN/PDF Validation Workflow

Place one or more official FIN/PDF documents inside:

incoming_fin/

Then run:

python scripts/read_fin_pdf.py

The script generates:

validation/fin_pdf_review.md

This file summarizes extracted fields and provides a human validation section where the reviewer can record:

- Human decision
- Validator notes
- Manual corrections
- Confirmation of key product conditions

Uploaded PDFs are intentionally ignored by Git and should not be committed to the repository.

---

## Approved Dataset Update Workflow

When a source change requires a controlled dataset update, generate proposed updates:

python scripts/propose_dataset_updates.py

Review the generated file:

validation/proposed_updates.csv

Approve only the rows that should update the dataset, then run:

python scripts/apply_approved_updates.py

This ensures that dataset changes are not applied automatically without human approval.

---

## Portfolio Relevance

This project was built as a practical banking and data analysis portfolio project.

It demonstrates:

- Financial product analysis
- Python and pandas data processing
- Streamlit app development
- Financial calculation logic
- Data quality awareness
- Source monitoring
- Human-in-the-loop validation
- Basic data governance principles
- Clear documentation and versioned releases

The goal is not only to compare deposit returns, but also to simulate a realistic workflow where financial product information is checked against official sources before being used for analysis.

---

## Example Use Cases

This project can be used as a demonstration of:

- Banking analytics
- Retail banking product comparison
- Financial data processing
- Product monitoring
- Human validation workflows
- Data governance in financial services
- Python-based portfolio work for banking and finance roles

---

## Limitations

- Dataset is manually curated
- Deposit rates and conditions may change at any time
- Some official PDFs may require manual confirmation due to formatting limitations
- The app does not provide real-time financial product updates
- Calculations are simplified estimates
- Account maintenance costs, exemptions, fees or specific tax circumstances may not be fully reflected
- This project is educational and informational only

---

## Disclaimer

This project is for educational and informational purposes only.

It does not constitute financial advice, investment advice, tax advice or a recommendation to subscribe to any financial product.

Deposit rates, conditions, eligibility criteria, tax treatment and account costs may change at any time.

Always confirm the latest information directly with the official bank documentation before making any financial decision.

---

## License

This project is licensed under the MIT License.
