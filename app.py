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

st.markdown(
    '<div class="main-title">🏦 Portugal Term Deposit Comparator</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Compare Portuguese term deposits by estimated net yield, maturity, eligibility criteria and liquidity conditions.</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Dataset metadata and disclaimer
# ------------------------------------------------------------

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
# Project Highlights Section
# ------------------------------------------------------------

st.markdown("## Project Highlights")

highlight_col1, highlight_col2, highlight_col3, highlight_col4 = st.columns(4)

with highlight_col1:
    st.info(
        """
        **Banking Analytics**  
        Compares Portuguese term deposits using financial product criteria.
        """
    )

with highlight_col2:
    st.success(
        """
        **Net Yield Simulation**  
        Estimates gross interest, tax impact, net interest and final amount.
        """
    )

with highlight_col3:
    st.warning(
        """
        **Eligibility Alerts**  
        Flags new client rules, new money requirements and liquidity conditions.
        """
    )

with highlight_col4:
    st.info(
        """
        **Human Validation**  
        Uses official source tracking and manual review before dataset updates.
        """
    )

st.divider()


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
# Selected deposit simulation
# ------------------------------------------------------------

st.markdown("## Selected Deposit Simulation")

selection_df = ranking.copy().reset_index(drop=True)


def build_deposit_label(row: pd.Series) -> str:
    bank_name = row.get(bank_col_r, "N/A") if bank_col_r else "N/A"
    product_name = row.get(product_col_r, "N/A") if product_col_r else "N/A"
    tanb_value = format_percentage(row.get(tanb_col_r)) if tanb_col_r else "N/A"
    net_value = format_currency(row.get(net_interest_col)) if net_interest_col else "N/A"

    return f"{bank_name} — {product_name} | TANB {tanb_value} | Net interest {net_value}"


selection_df["Deposit Selection Label"] = selection_df.apply(build_deposit_label, axis=1)

selected_label = st.selectbox(
    "Select deposit to simulate",
    options=selection_df["Deposit Selection Label"].tolist(),
    index=0,
)

selected_index = selection_df[
    selection_df["Deposit Selection Label"] == selected_label
].index[0]

selected_deposit = selection_df.loc[selected_index]

selected_bank_name = selected_deposit.get(bank_col_r, "N/A") if bank_col_r else "N/A"
selected_product_name = selected_deposit.get(product_col_r, "N/A") if product_col_r else "N/A"
selected_tanb = selected_deposit.get(tanb_col_r, "N/A") if tanb_col_r else "N/A"
selected_net_interest = selected_deposit.get(net_interest_col, "N/A") if net_interest_col else "N/A"
selected_final_amount = selected_deposit.get(final_amount_col, "N/A") if final_amount_col else "N/A"

st.markdown(
    f"""
    <div class="simulation-card">
        <div class="card-title">{selected_bank_name} — {selected_product_name}</div>
        <div class="card-line"><strong>Capital:</strong> {format_currency(capital)}</div>
        <div class="card-line"><strong>Maturity:</strong> {maturity_months} months</div>
        <div class="card-line"><strong>TANB:</strong> {format_percentage(selected_tanb)}</div>
        <div class="card-line"><strong>Estimated Net Interest:</strong> {format_currency(selected_net_interest)}</div>
        <div class="card-line"><strong>Estimated Final Amount:</strong> {format_currency(selected_final_amount)}</div>
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

    if bank_col_r:
        chart_df["Display Label"] = (
            chart_df[bank_col_r].astype(str)
            + " — "
            + chart_df[product_col_r].astype(str)
        )
    else:
        chart_df["Display Label"] = chart_df[product_col_r].astype(str)

    chart_df = chart_df.sort_values(net_interest_col, ascending=True)

    fig = px.bar(
        chart_df,
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
        height=max(400, len(chart_df) * 45),
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------
# Product details, notes and official sources
# ------------------------------------------------------------

st.markdown("## Product Details, Notes and Sources")

for _, row in ranking.iterrows():
    bank_name = row.get(bank_col_r, "N/A") if bank_col_r else "N/A"
    product_name = row.get(product_col_r, "N/A") if product_col_r else "N/A"

    with st.expander(f"{bank_name} — {product_name}"):
        detail_col1, detail_col2, detail_col3 = st.columns(3)

        with detail_col1:
            if tanb_col_r:
                st.metric("TANB", format_percentage(row.get(tanb_col_r)))
            if maturity_col_r:
                st.write(f"**Maturity:** {row.get(maturity_col_r)} months")

        with detail_col2:
            if gross_interest_col:
                st.metric("Estimated Gross Interest", format_currency(row.get(gross_interest_col)))
            if tax_col:
                st.metric("Estimated Tax", format_currency(row.get(tax_col)))

        with detail_col3:
            if net_interest_col:
                st.metric("Estimated Net Interest", format_currency(row.get(net_interest_col)))
            if final_amount_col:
                st.metric("Estimated Final Amount", format_currency(row.get(final_amount_col)))

        if alerts_col:
            st.write("**Alerts:**")
            st.write(row.get(alerts_col, "No alerts"))

        if notes_col:
            st.write("**Notes / Conditions:**")
            st.write(row.get(notes_col, "No notes available"))

        if source_col:
            source_value = row.get(source_col, "")
            if pd.notna(source_value) and str(source_value).strip():
                st.write("**Official Source / Reference:**")
                st.write(source_value)


# ------------------------------------------------------------
# Downloads
# ------------------------------------------------------------

st.markdown("## Downloads")

download_col1, download_col2 = st.columns(2)

with download_col1:
    csv_data = ranking.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Download ranking as CSV",
        data=csv_data,
        file_name="term_deposit_ranking.csv",
        mime="text/csv",
    )

with download_col2:
    excel_data = to_excel_bytes(ranking)

    st.download_button(
        label="Download ranking as Excel",
        data=excel_data,
        file_name="term_deposit_ranking.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.divider()

st.markdown(
    """
    <div class="small-muted">
    MVP prototype built with Python, pandas, Streamlit and Plotly.  
    Data should always be validated against official bank sources before any financial decision.
    </div>
    """,
    unsafe_allow_html=True,
)
