# Portugal Term Deposit Comparator

A Python-based tool to compare Portuguese term deposits by net yield, maturity, eligibility criteria and liquidity conditions.

This project was created as a practical banking and data analysis mini-project, combining financial product analysis, Python, pandas, Streamlit, Plotly and an interactive Google Colab prototype.

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

---

## Market Scope

The initial MVP focuses on:

- Portuguese banks
- Banks with a physical or established presence in Portugal
- Selected online banks with relevant offering for Portuguese residents

The project intentionally excludes broad EU digital-only banks without a clear focus on the Portuguese retail deposit market.

---

## Current Features

- Cleaned dataset of Portuguese term deposits
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

---

## Dataset

The main dataset used in this project is:

`data/depositos_prazo_core_portugal_corrigido.csv`

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

The dataset was manually cleaned and structured from publicly available term deposit information and quickly validated against official bank sources where possible.

---

## Financial Logic

The gross interest is estimated using:

`Gross interest = Capital × TANB × Maturity / 12`

Where:

`Capital = amount invested`  
`TANB = annual nominal gross rate`  
`Maturity = number of months`

The estimated tax is calculated using:

`Estimated tax = Gross interest × Tax rate`

The net interest is calculated using:

`Net interest = Gross interest - Estimated tax`

The final estimated amount is:

`Final amount = Capital + Net interest`

For the MVP, the default tax rate used is:

`28%`

This corresponds to the standard withholding tax assumption for Portuguese resident individuals.

---

## Example Use Case

Example input:

`Capital: 10,000 EUR`  
`Maturity: 12 months`  
`Bank: All banks`  
`Accept new client products: Yes`  
`Accept new money products: Yes`  
`Require early withdrawal: No`

Example output:

`Bank | Product | Maturity | TANB | Net Interest | Final Amount | Alerts`

The tool ranks the eligible deposits by estimated net interest.

---

## Alerts

The tool automatically generates alerts such as:

- New clients only
- New money only
- Early withdrawal: check notes
- Maximum investment limit
- Partial validation

These alerts help identify important product conditions beyond the headline interest rate.

---

## Repository Structure

Current structure:

```text
portugal-term-deposit-comparator/
│
├── app.py
├── data/
│   └── depositos_prazo_core_portugal_corrigido.csv
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
├── src/
│   └── calculator.py
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
- GitHub

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

- Simulation summary
- Ranking table
- Interactive horizontal chart with Plotly
- Visual selected deposit simulation card
- Selectable deposit simulation panel
- Product notes and official source links
- CSV download button
- Excel download button

---

## Export Ranking to CSV

The project includes an example script to export the ranking output to a CSV file.

Run:

```bash
python examples/export_ranking.py
```

This will generate:

```text
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

```text
outputs/ranking_output.xlsx
```

The exported file includes the ranked term deposits based on the selected sample scenario.

---

## Python Module

The main calculation logic is available in:

```text
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

`notebooks/portugal-term-deposit-comparator.ipynb`

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
- Add manual validation workflow
- Add automated change detection from official sources
- Add comparison between term deposits and savings certificates
- Add historical tracking of rate changes
- Add product-level confidence score
- Add deposit guarantee scheme information
- Add “no alerts only” filter
- Add real-time dataset update workflow
- Deploy versioned Streamlit releases

---

## Project Status

`MVP completed`

The current version includes a cleaned dataset, financial calculation logic, a reusable Python module, a basic usage example, CSV and Excel export functionality, a Streamlit simulator app, an interactive Plotly chart and a visual selected deposit simulation panel.

---

## Author

Ricardo Serôdio

Banking professional with experience in credit, wealth management, client advisory and retail banking operations.

GitHub project created as part of a practical portfolio focused on banking, finance, data analysis and Python.
