from io import BytesIO
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.calculator import load_data, prepare_data, compare_deposits


# ------------------------------------------------------------
# Paths and metadata
# ------------------------------------------------------------

METADATA_PATH = Path("data/metadata.json")


def load_metadata(path: Path = METADATA_PATH) -> dict:
    """Load dataset metadata used for app status and disclaimer."""
    if path.exists():
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    return {
        "dataset_name": "Portuguese Term Deposits Core Dataset",
        "reference_date": "Not available",
        "last_manual_validation": "Not available",
        "validation_status": "Not available",
        "market_scope": "Not available",
        "real_time_warning": "Dataset metadata is not available.",
        "disclaimer": (
            "This tool is for educational and informational purposes only. "
            "It does not constitute financial advice."
        ),
    }


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Find the first matching column from a list of possible column names."""
    for col in candidates:
        if col in df.columns:
            return col
    return None


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Convert a dataframe to Excel bytes for Streamlit download."""
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Ranking")

    return output.getvalue()


def format_currency(value) -> str:
    """Format numeric values as EUR."""
    try:
        return f"{float(value):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "N/A"


def format_percentage(value) -> str:
    """Format numeric values as percentage."""
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return "N/A"


# ------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="Portugal Term Deposit Comparator",
    page_icon="🏦",
    layout="wide",
)


# ------------------------------------------------------------
# Custom CSS
# ------------------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 17px;
        color: #B0B0B0;
        margin-bottom: 25px;
    }

    .small-muted {
        font-size: 13px;
        color: #9CA3AF;
    }

    .simulation-card {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 24px;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .card-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .card-line {
        font-size: 15px;
        margin-bottom: 6px;
    }

    .validation-box {
        border: 1px solid #374151;
        border-radius: 14px;
        padding: 18px;
        background-color: #0F172A;
        margin-bottom: 15px;
    }

    .section-divider {
        margin-top: 25px;
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Load metadata and data
# ------------------------------------------------------------

metadata = load_metadata()

df = load_data()
df = prepare_data(df)


# ------------------------------------------------------------
# Sidebar inputs
# ------------------------------------------------------------

st.sidebar.header("Simulation Inputs")

capital = st.sidebar.number_input(
    "Capital to invest (€)",
    min_value=0.0,
    value=10000.0,
    step=500.0,
    format="%.2f",
)

maturity_col = find_column(df, ["Prazo (meses)", "Maturity", "Maturity (months)"])
bank_col = find_column(df, ["Banco", "Bank"])

if maturity_col:
    available_maturities = sorted(df[maturity_col].dropna().unique())
else:
    available_maturities = [3, 6, 12, 24]

maturity_months = st.sidebar.selectbox(
    "Maturity (months)",
    options=available_maturities,
    index=available_maturities.index(12) if 12 in available_maturities else 0,
)

if bank_col:
    available_banks = ["All banks"] + sorted(df[bank_col].dropna().astype(str).unique().tolist())
else:
    available_banks = ["All banks"]

selected_bank = st.sidebar.selectbox(
    "Bank",
    options=available_banks,
)

require_early_withdrawal = st.sidebar.checkbox(
    "Require early withdrawal option",
    value=False,
)

accept_new_clients_only = st.sidebar.checkbox(
    "Accept products for new clients only",
    value=True,
)

accept_new_money_only = st.sidebar.checkbox(
    "Accept products for new money only",
    value=True,
)

top_n = st.sidebar.slider(
    "Number of results",
    min_value=3,
    max_value=20,
    value=10,
)


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.markdown('<div class="main-title">🏦 Portugal Term Deposit Comparator</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">Compare Portuguese term deposits by estimated net yield, maturity, eligibility criteria and liquidity conditions.</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Dataset metadata and disclaimer
# ------------------------------------------------------------

with st.container():
    meta_col1, meta_col2, meta_col3 = st.columns(3)

    with meta_col1:
        st.metric(
            label="Dataset Reference Date",
            value=metadata.get("reference_date", "Not available"),
        )

    with meta_col2:
        st.metric(
            label="Last Manual Validation",
            value=metadata.get("last_manual_validation", "Not available"),
        )

    with meta_col3:
        st.metric(
            label="Dataset Status",
            value="Curated dataset",
        )

st.info(
    f"""
    **Validation status:** {metadata.get("validation_status", "Not available")}  
    **Market scope:** {metadata.get("market_scope", "Not available")}
    """
)

st.warning(
    metadata.get(
        "disclaimer",
        "This tool is for educational and informational purposes only. It does not constitute financial advice.",
    )
)


# ------------------------------------------------------------
# Data Quality & Human Validation Section
# ------------------------------------------------------------

st.markdown("## Data Quality & Human Validation")

st.markdown(
    """
    This section summarizes the dataset governance and validation status used by this tool.

    The app uses a manually curated dataset and does **not** automatically update deposit
    rates or product conditions without human review.
    """
)

dq_col1, dq_col2, dq_col3 = st.columns(3)

with dq_col1:
    st.metric(
        label="Dataset Reference Date",
        value=metadata.get("reference_date", "Not available"),
    )

with dq_col2:
    st.metric(
        label="Last Manual Validation",
        value=metadata.get("last_manual_validation", "Not available"),
    )

with dq_col3:
    st.metric(
        label="Validation Status",
        value="Human-reviewed",
    )

dq_col4, dq_col5 = st.columns(2)

with dq_col4:
    st.info(
        """
        **Official Source Tracking:** Enabled  
        Product sources are tracked through `data/source_links.csv`.
        """
    )

with dq_col5:
    st.success(
        """
        **Human Validation Workflow:** Enabled  
        Source checks generate validation reports before any dataset update.
        """
    )

with st.expander("How the validation workflow works"):
    st.markdown(
        """
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

        The monitoring script is located at:

        ```bash
        scripts/monitor_sources.py
        ```

        Official source links are stored in:

        ```bash
        data/source_links.csv
        ```

        Validation reports are generated locally under:

        ```bash
        validation/
        ```

        These reports are excluded from version control and should be reviewed manually before updating the main dataset.
        """
    )

st.divider()


# ------------------------------------------------------------
# Run comparison
# ------------------------------------------------------------

ranking = compare_deposits(
    df=df,
    capital=capital,
    maturity_months=maturity_months,
    selected_bank=selected_bank,
    require_early_withdrawal=require_early_withdrawal,
    accept_new_clients_only=accept_new_clients_only,
    accept_new_money_only=accept_new_money_only,
    top_n=top_n,
)


# ------------------------------------------------------------
# Empty state
# ------------------------------------------------------------

if ranking is None or ranking.empty:
    st.error("No eligible deposits found for the selected criteria.")
    st.stop()


# ------------------------------------------------------------
# Column detection after calculation
# ------------------------------------------------------------

bank_col_r = find_column(ranking, ["Banco", "Bank"])
product_col_r = find_column(ranking, ["Produto", "Product"])
maturity_col_r = find_column(ranking, ["Prazo (meses)", "Maturity", "Maturity (months)"])
tanb_col_r = find_column(ranking, ["TANB (%)", "TANB", "Gross Rate"])
net_interest_col = find_column(
    ranking,
    [
        "Juro líquido estimado (€)",
        "Net Interest",
        "Estimated Net Interest",
        "Estimated net interest",
    ],
)
final_amount_col = find_column(
    ranking,
    [
        "Montante final estimado (€)",
        "Final Amount",
        "Estimated Final Amount",
        "Estimated final amount",
    ],
)
gross_interest_col = find_column(
    ranking,
    [
        "Juro bruto estimado (€)",
        "Gross Interest",
        "Estimated Gross Interest",
    ],
)
tax_col = find_column(
    ranking,
    [
        "IRS estimado (€)",
        "Estimated Tax",
        "Tax",
    ],
)
alerts_col = find_column(ranking, ["Alertas", "Alerts"])
notes_col = find_column(ranking, ["Notas / condições", "Notas", "Notes", "Conditions"])
source_col = find_column(
    ranking,
    [
        "Fonte oficial / referência",
        "Fonte oficial",
        "Official source",
        "Source",
        "Reference",
    ],
)


# ------------------------------------------------------------
# Simulation summary
# ------------------------------------------------------------

st.markdown("## Simulation Summary")

summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

with summary_col1:
    st.metric("Capital", format_currency(capital))

with summary_col2:
    st.metric("Maturity", f"{maturity_months} months")

with summary_col3:
    st.metric("Bank Filter", selected_bank)

with summary_col4:
    st.metric("Eligible Results", len(ranking))


# ------------------------------------------------------------
# Selected deposit card
# ------------------------------------------------------------

best = ranking.iloc[0]

best_bank = best.get(bank_col_r, "N/A") if bank_col_r else "N/A"
best_product = best.get(product_col_r, "N/A") if product_col_r else "N/A"
best_tanb = best.get(tanb_col_r, "N/A") if tanb_col_r else "N/A"
best_net_interest = best.get(net_interest_col, "N/A") if net_interest_col else "N/A"
best_final_amount = best.get(final_amount_col, "N/A") if final_amount_col else "N/A"

st.markdown("## Selected Deposit Simulation")

st.markdown(
    f"""
    <div class="simulation-card">
        <div class="card-title">{best_bank} — {best_product}</div>
        <div class="card-line"><strong>Capital:</strong> {format_currency(capital)}</div>
        <div class="card-line"><strong>Maturity:</strong> {maturity_months} months</div>
        <div class="card-line"><strong>TANB:</strong> {format_percentage(best_tanb)}</div>
        <div class="card-line"><strong>Estimated Net Interest:</strong> {format_currency(best_net_interest)}</div>
        <div class="card-line"><strong>Estimated Final Amount:</strong> {format_currency(best_final_amount)}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Ranking results
# ------------------------------------------------------------

st.markdown("## Ranking Results")

ranking_display = ranking.copy()

st.dataframe(
    ranking_display,
    use_container_width=True,
    hide_index=True,
)


# ------------------------------------------------------------
# Chart
# ------------------------------------------------------------

if net_interest_col and product_col_r:
    st.markdown("## Net Interest Comparison")

    chart_df = ranking.copy()
    chart_df["Display Label"] = (
        chart_df[bank_col_r].astype(str) + " — " + chart_df[product_col_r].astype(str)
        if bank_col_r
        else chart_df[product_col_r].astype(str)
    )

    fig = px.bar(
        chart_df.sort_values(net_interest_col, ascending=True),
        x=net_interest_col,
        y="Display Label",
        orientation="h",
        title="Estimated Net Interest by Product",
        labels={
            net_interest_col: "Estimated Net Interest (€)",
            "Display Label": "Deposit Product",
        },
    )

    fig.update_layout(
        height=max(400, len(chart_df_
