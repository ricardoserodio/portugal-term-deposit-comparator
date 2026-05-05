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

    ranking_table = ranking[
        [
            "Banco",
            "Produto",
            "Prazo (meses)",
            "TANB (%)",
            "Juro líquido estimado (€)",
            "Montante final estimado (€)",
            "Alertas",
        ]
    ]

    st.dataframe(
        ranking_table,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Net Interest Comparison")

    chart_data = ranking_table.copy()
    chart_data["Deposit"] = chart_data["Banco"] + " — " + chart_data["Produto"]
    chart_data = chart_data.set_index("Deposit")

    st.bar_chart(chart_data["Juro líquido estimado (€)"])

    st.subheader("Selected Deposit Simulation")

    deposit_options = {}

    for index, row in ranking.iterrows():
        label = (
            f'{row["Banco"]} — {row["Produto"]} | '
            f'{row["TANB (%)"]:.2f}% | '
            f'{int(row["Prazo (meses)"])} months | '
            f'Net interest: {row["Juro líquido estimado (€)"]:.2f} €'
        )
        deposit_options[label] = index

    selected_label = st.selectbox(
        "Select deposit to simulate",
        options=list(deposit_options.keys()),
    )

    selected_index = deposit_options[selected_label]
    selected = ranking.loc[selected_index]

    sim_col1, sim_col2, sim_col3 = st.columns(3)

    sim_col1.write(f'**Bank:** {selected["Banco"]}')
    sim_col1.write(f'**Product:** {selected["Produto"]}')
    sim_col1.write(f"**Capital invested:** {capital:,.2f} €")

    sim_col2.write(f'**Maturity:** {int(selected["Prazo (meses)"])} months')
    sim_col2.write(f'**TANB:** {selected["TANB (%)"]:.2f}%')
    sim_col2.write(f'**Alerts:** {selected["Alertas"]}')

    sim_col3.write(f'**Gross interest:** {selected["Juro bruto estimado (€)"]:.2f} €')
    sim_col3.write(f'**Estimated tax:** {selected["IRS estimado (€)"]:.2f} €')
    sim_col3.write(f'**Net interest:** {selected["Juro líquido estimado (€)"]:.2f} €')
    sim_col3.write(f'**Final amount:** {selected["Montante final estimado (€)"]:.2f} €')

    notes = selected.get("Notas / condições", "")
    source = selected.get("Fonte oficial / referência", "")

    with st.expander("Selected deposit notes and official source", expanded=True):
        if notes:
            st.write(f"**Notes / conditions:** {notes}")
        else:
            st.write("**Notes / conditions:** Not available")

        if source:
            st.markdown(f"**Official source / reference:** [Open official source]({source})")
        else:
            st.write("**Official source / reference:** Not available")

    st.subheader("Product Details, Notes and Sources")

    for _, row in ranking.iterrows():
        title = f'{row["Banco"]} — {row["Produto"]} | {row["TANB (%)"]:.2f}% | {int(row["Prazo (meses)"])} months'

        with st.expander(title):
            st.write(f'**Gross interest:** {row["Juro bruto estimado (€)"]:.2f} €')
            st.write(f'**Estimated tax:** {row["IRS estimado (€)"]:.2f} €')
            st.write(f'**Estimated net interest:** {row["Juro líquido estimado (€)"]:.2f} €')
            st.write(f'**Estimated final amount:** {row["Montante final estimado (€)"]:.2f} €')
            st.write(f'**Alerts:** {row["Alertas"]}')

            row_notes = row.get("Notas / condições", "")
            row_source = row.get("Fonte oficial / referência", "")

            if row_notes:
                st.write(f"**Notes / conditions:** {row_notes}")
            else:
                st.write("**Notes / conditions:** Not available")

            if row_source:
                st.markdown(f"**Official source / reference:** [Open official source]({row_source})")
            else:
                st.write("**Official source / reference:** Not available")

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
