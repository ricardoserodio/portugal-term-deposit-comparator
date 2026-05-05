# Portugal Term Deposit Comparator

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![pandas](https://img.shields.io/badge/pandas-Data%20Analysis-blue)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-purple)
![Data Governance](https://img.shields.io/badge/Data%20Governance-Human%20Validation-green)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

A Python-based tool to compare Portuguese term deposits by estimated net yield, maturity, eligibility criteria and liquidity conditions.

This project was created as a practical banking and data analysis mini-project, combining financial product analysis, Python, pandas, Streamlit, Plotly, Google Colab and a human-in-the-loop validation workflow.

---

## Project Overview

The goal of this project is to compare term deposit products available in Portugal and estimate the net return for a given investment amount and maturity.

The tool allows users to filter deposits based on:

- Investment amount
- Maturity
- Bank
- New client eligibility
- New money requirements
- Early withdrawal conditions
- Estimated withholding tax

The output ranks eligible deposits by estimated net interest.

The project is designed not only as a simulator, but also as a practical example of banking product analysis, data cleaning, financial calculation logic and data governance.

---

## Market Scope

The initial MVP focuses on:

- Portuguese banks
- Banks with a physical or established presence in Portugal
- Selected online banks with relevant offers for Portuguese residents

The project intentionally excludes broad EU digital-only banks without a clear focus on the Portuguese retail deposit market.

---

## Current Features

- Cleaned dataset of Portuguese term deposits
- Dataset metadata and validation status display
- Filtering by investment amount
- Filtering by maturity
- Bank-level filtering
- Filtering by new client requirement
- Filtering by new money requirement
- Filtering by early withdrawal availability
- Gross interest calculation
- Estimated tax calculation
- Net interest calculation
- Final amount estimation
- Automatic condition alerts
- Interactive Google Colab prototype
- Reusable Python calculation module
- Basic usage example script
- Export ranking results to CSV
- Export ranking results to Excel
- Streamlit simulator app
- Interactive Plotly chart
- Visual selected deposit simulation card
- Product notes and official source links
- Dataset metadata file
- Source links file for official references
- Human validation workflow
- Source monitoring script
- Local validation report generation

---

## Dataset

The main dataset used in this project is:

```bash
data/depositos_prazo_core_portugal_corrigido.csv
```

The dataset includes fields such as:

- Bank
- Product
- Maturity
- TANB
- Minimum investment
- Maximum investment
- New clients only
- New money only
- Early withdrawal
- Tax applicability
- Notes / conditions
- Validation status
- Official source / reference
- Reference date

The dataset was manually cleaned and structured from publicly available term deposit information and validated against official bank sources where possible.

The Streamlit app uses this curated dataset as the main source of product information.

---

## Dataset Metadata

The project includes a metadata file:

```bash
data/metadata.json
```

This file stores key information used by the Streamlit app, including:

- Dataset name
- Data reference date
- Last manual validation date
- Validation status
- Market scope
- Real-time data warning
- Disclaimer text

This allows the app to display clear dataset status information without hardcoding dates or disclaimers directly in the application code.

The Streamlit app reads this metadata file automatically and displays the information at the top of the interface.

---

## Human Validation Workflow

This project includes a human-in-the-loop validation workflow to improve data quality and reduce the risk of outdated or incorrect deposit information.

The application does **not** automatically update the main dataset based on web changes. Instead, it follows a controlled validation process:

```text
Official bank sources
        ↓
Source monitoring script
        ↓
Validation report
        ↓
Human review
        ↓
Manual dataset update
        ↓
Streamlit app uses validated data only
```

This approach is intentional. Deposit rates, eligibility criteria, minimum and maximum amounts, and early withdrawal conditions can change frequently. A fully automatic update process could introduce incorrect or misleading information into the application.

The project therefore uses a conservative data governance approach:

1. Monitor official sources.
2. Generate validation reports.
3. Review changes manually.
4. Update the curated dataset only after human confirmation.

This makes the project more aligned with real banking data governance, product monitoring and quality control practices.

---

## Source Links

Official product pages, FIN documents, pricing sheets and reference URLs are stored in:

```bash
data/source_links.csv
```

This file includes:

- Bank name
- Product name
- Source type
- Official URL
- Fields to validate
- Previous audit status
- Human validation notes

The file uses `|` as a separator to avoid parsing issues caused by commas in descriptions, notes or source text.

Example fields monitored:

- TANB
- Maturity
- Minimum investment
- Maximum investment
- New client conditions
- New money conditions
- Early withdrawal rules
- Renewal rules

---

## Source Monitoring Script

The monitoring script is located at:

```bash
scripts/monitor_sources.py
```

It reads the official source links and generates a validation report.

Run:

```bash
python scripts/monitor_sources.py
```

The script does **not** change the curated dataset. It only collects source information and creates a report for manual review.

The script uses:

- `requests` to access official bank URLs
- `beautifulsoup4` to extract readable text from HTML pages
- `pandas` to structure and export the validation report

---

## Validation Reports

Generated reports are stored locally in:

```bash
validation/
```

Example:

```bash
validation/validation_report_YYYYMMDD_HHMM.csv
```

Each report includes:

- Detection date
- Bank
- Product
- Source type
- Official link
- Fields to validate
- Previous audit status
- Previous audit notes
- Extracted source text
- Validation status
- Human decision
- Suggested action
- Validator notes

Validation reports are intentionally excluded from version control through `.gitignore`, except for the `.gitkeep` placeholder.

This avoids committing temporary or recurring validation outputs while keeping the folder structure available in the repository.

---

## Financial Logic

The gross interest is estimated using:

```text
Gross interest = Capital × TANB × Maturity / 12
```

Where:

- Capital = amount invested
- TANB = annual nominal gross rate
- Maturity = number of months

The estimated tax is calculated using:

```text
Estimated tax = Gross interest × Tax rate
```

The net interest is calculated using:

```text
Net interest = Gross interest - Estimated tax
```

The final estimated amount is:

```text
Final amount = Capital + Net interest
```

For the MVP, the default tax rate used is:

```text
28%
```

This corresponds to the standard withholding tax assumption for Portuguese resident individuals.

---

## Example Use Case

Example input:

```text
Capital: 10,000 EUR
Maturity: 12 months
Bank: All banks
Accept new client products: Yes
Accept new money products: Yes
Require early withdrawal: No
```

Example output:

```text
Bank | Product | Maturity | TANB | Net Interest | Final Amount | Alerts
```

The tool ranks the eligible deposits by estimated net interest.

---

## Alerts

The tool automatically generates alerts such as:

- New clients only
- New money only
- Early withdrawal: check notes
- Maximum investment limit
- Partial validation
- Conditions require manual confirmation

These alerts help identify important product conditions beyond the headline interest rate.

---

## Repository Structure

Current structure:

```text
portugal-term-deposit-comparator/
│
├── app.py
│
├── data/
│   ├── depositos_prazo_core_portugal_corrigido.csv
│   ├── metadata.json
│   └── source_links.csv
│
├── examples/
│   ├── basic_usage.py
│   ├── export_ranking.py
│   └── export_ranking_excel.py
│
├── notebooks/
│   └── portugal-term-deposit-comparator.ipynb
│
├── outputs/
│   └── .gitkeep
│
├── scripts/
│   └── monitor_sources.py
│
├── src/
│   └── calculator.py
│
├── validation/
│   └── .gitkeep
│
├── .gitignore
├── README.md
├── requirements.txt
└── LICENSE
```

---

## Technologies Used

- Python
- pandas
- NumPy
- Google Colab
- ipywidgets
- Streamlit
- Plotly
- openpyxl
- requests
- beautifulsoup4
- GitHub
- Codespaces

---

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/ricardoserodio/portugal-term-deposit-comparator.git
cd portugal-term-deposit-comparator
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the basic example

```bash
python examples/basic_usage.py
```

This will load the cleaned dataset from the `data/` folder and generate a ranking of eligible term deposits for a sample investment scenario.

---

## Run the Streamlit App

The project includes a Streamlit simulator app.

Run:

```bash
streamlit run app.py
```

The app allows users to simulate term deposit rankings using:

- Investment amount
- Maturity
- Bank filter
- Early withdrawal preference
- New client product eligibility
- New money product eligibility
- Number of results to display

The app also includes:

- Dataset reference date and validation status
- Strong visible disclaimer
- Simulation summary
- Ranking table
- Interactive horizontal chart with Plotly
- Visual selected deposit simulation card
- Selectable deposit simulation panel
- Product notes and official source links
- CSV download button
- Excel download button

---

## Run the Human Validation Workflow

To generate a validation report from official bank sources, run:

```bash
python scripts/monitor_sources.py
```

This will read:

```bash
data/source_links.csv
```

And generate a local report under:

```bash
validation/
```

Example output:

```bash
validation/validation_report_YYYYMMDD_HHMM.csv
```

The generated report should be reviewed manually before making any change to the main dataset.

---

## Export Ranking to CSV

The project includes an example script to export the ranking output to a CSV file.

Run:

```bash
python examples/export_ranking.py
```

This will generate:

```bash
outputs/ranking_output.csv
```

The exported file includes the ranked term deposits based on the selected sample scenario.

---

## Export Ranking to Excel

The project also includes an example script to export the ranking output to an Excel file.

Run:

```bash
python examples/export_ranking_excel.py
```

This will generate:

```bash
outputs/ranking_output.xlsx
```

The exported file includes the ranked term deposits based on the selected sample scenario.

---

## Python Module

The main calculation logic is available in:

```bash
src/calculator.py
```

The module includes functions to:

- Load the dataset
- Prepare numeric and text fields
- Filter deposits by eligibility criteria
- Filter deposits by bank
- Calculate gross interest
- Estimate withholding tax
- Calculate net interest
- Generate product alerts
- Rank deposits by estimated net return

---

## Example Code

```python
from src.calculator import load_data, prepare_data, compare_deposits

df = load_data()
df = prepare_data(df)

ranking = compare_deposits(
    df=df,
    capital=10000,
    maturity_months=12,
    selected_bank="All banks",
    require_early_withdrawal=False,
    accept_new_clients_only=True,
    accept_new_money_only=True,
    top_n=10,
)

print(ranking)
```

---

## Notebook

The interactive prototype is available in:

```bash
notebooks/portugal-term-deposit-comparator.ipynb
```

The notebook includes:

- Data loading
- Data cleaning
- Financial calculations
- Filtering logic
- Alert generation
- Interactive widgets for user input

---

## Limitations

This project is an educational and analytical prototype.

Important limitations:

- Deposit conditions may change frequently.
- Data should be verified with each bank before any financial decision.
- Some products may have additional account maintenance costs.
- Some rates may be promotional or limited to specific customer segments.
- Early withdrawal conditions may vary and should be checked in the official documentation.
- The tax calculation is simplified and assumes a standard 28% withholding tax.
- The project does not account for all possible tax situations or exemptions.
- The dataset may not reflect real-time product changes.
- The metadata status does not replace validation against official bank documentation.
- The source monitoring script does not guarantee automatic detection of all product changes.
- Validation reports require human review before any dataset update.

---

## Disclaimer

This project is for educational and informational purposes only.

It does not constitute financial advice, investment advice, tax advice or a recommendation to subscribe to any financial product.

Before making any financial decision, users should always confirm the latest product conditions, official rate sheets, pre-contractual information and tax implications directly with the relevant bank or a qualified professional.

---

## Future Improvements

Planned improvements include:

- Add account cost impact on net return
- Add source tracking per product
- Add update date per product
- Improve manual validation workflow
- Add automated change detection from official sources
- Compare current source snapshot against previous source snapshot
- Add comparison between term deposits and savings certificates
- Add historical tracking of rate changes
- Add product-level confidence score
- Add deposit guarantee scheme information
- Add “no alerts only” filter
- Add validation dashboard inside the Streamlit app
- Deploy versioned Streamlit releases

---

## Project Status

MVP completed.

The current version includes a cleaned dataset, dataset metadata, financial calculation logic, a reusable Python module, a basic usage example, CSV and Excel export functionality, a Streamlit simulator app, an interactive Plotly chart, a visual selected deposit simulation panel, source link tracking and a human validation workflow.

---

## Author

Ricardo Serôdio

Banking professional with experience in credit, wealth management, client advisory and retail banking operations.

GitHub project created as part of a practical portfolio focused on banking, finance, data analysis and Python.
