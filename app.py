from io import BytesIO

import streamlit as st

from src.calculator import load_data, prepare_data, compare_deposits


st.set_page_config(
    page_title="Portugal Term Deposit Comparator",
    page_icon="🏦",
    layout="wide",
)


st.title("🏦 Portugal Term Deposit Comparator")

st.write(
    """
    Compare Portuguese term deposits by estimated net yield, maturity,
    eligibility criteria and liquidity conditions.
    """
)

st.warning(
    """
    This tool is for educational and informational purposes only.
    It does not constitute financial advice. Always confirm deposit conditions
    directly with the official bank documentation before making any decision.
    """
)


@st.cache_data
def get_data():
    df = load_data()
    return prepare_data(df)


df = get_data()

st.sidebar.header("Simulation Inputs")

capital = st.sidebar.number_input(
    "Capital to invest (€)",
    min_value=0.0,
    value=10000.0,
    step=500.0,
)

available_maturities = sorted(df["Prazo (meses)"].dropna().unique())

maturity_months = st.sidebar.selectbox(
    "Maturity (months)",
    available_maturities,
    index=available_maturities.index(12) if 12 in available_maturities else 0,
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

ranking = compare_deposits(
    df=df,
    capital=capital,
    maturity_months=maturity_months,
    require_early_withdrawal=require_early_withdrawal,
    accept_new_clients_only=accept_new_clients_only,
    accept_new_money_only=accept_new_money_only,
    top_n=top_n,
)

st.subheader("Simulation Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)

summary_col1.metric("Capital", f"{capital:,.2f} €")
summary_col2.metric("Maturity", f"{int(maturity_months)} months")
summary_col3.metric("Results shown", top_n)

summary_col4, summary_col5, summary_col6 = st.columns(3)

summary_col4.metric(
    "Early withdrawal required",
    "Yes" if require_early_withdrawal else "No",
)

summary_col5.metric(
    "New client products accepted",
    "Yes" if accept_new_clients_only else "No",
)

summary_col6.metric(
    "New money products accepted",
    "Yes" if accept_new_money_only else "No",
)

st.subheader("Ranking Results")

if ranking.empty:
    st.info("No eligible deposits found for the selected criteria.")
else:
    best = ranking.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Best Bank", best["Banco"])
    col2.metric("Best TANB", f'{best["TANB (%)"]:.2f}%')
    col3.metric("Estimated Net Interest", f'{best["Juro líquido estimado (€)"]:.2f} €')
    col4.metric("Estimated Final Amount", f'{best["Montante final estimado (€)"]:.2f} €')

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True,
    )

    csv = ranking.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Download ranking as CSV",
        data=csv,
        file_name="ranking_output.csv",
        mime="text/csv",
    )

    excel_buffer = BytesIO()

    ranking.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    st.download_button(
        label="Download ranking as Excel",
        data=excel_buffer,
        file_name="ranking_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.caption(
    "MVP prototype built with Python, pandas and Streamlit. Data should be validated against official bank sources."
)
