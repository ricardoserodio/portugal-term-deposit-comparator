from io import BytesIO

import plotly.express as px
import streamlit as st

from src.calculator import load_data, prepare_data, compare_deposits


st.set_page_config(
    page_title="Portugal Term Deposit Comparator",
    page_icon="🏦",
    layout="wide",
)


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
    .simulation-card {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 24px;
        margin-top: 10px;
        margin-bottom: 25px;
    }
    .card-title {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 12px;
        color: #FFFFFF;
    }
    .card-label {
        color: #9CA3AF;
        font-size: 13px;
        margin-bottom: 2px;
    }
    .card-value {
        color: #FFFFFF;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 14px;
    }
    .small-muted {
        color: #9CA3AF;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="main-title">🏦 Portugal Term Deposit Comparator</div>
    <div class="subtitle">
    Compare Portuguese term deposits by estimated net yield, maturity, eligibility criteria and liquidity conditions.
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    """
    **Data reference date:** 05 May 2026  
    **Dataset status:** Manually curated and partially validated against official sources.  
    **Market scope:** Portuguese banks, banks with physical/established presence in Portugal, and selected online banks relevant to Portuguese residents.  

    This dataset may not reflect real-time changes in deposit rates, conditions or eligibility criteria.
    """
)

st.warning(
    """
    **Disclaimer:** This tool is for educational and informational purposes only.  

    It does not constitute financial advice, investment advice, tax advice or a recommendation to subscribe to any financial product.  

    Deposit rates, conditions, eligibility criteria, tax treatment and account costs may change at any time.  
    Always confirm the latest information directly with the official bank documentation before making any financial decision.
    """
)


@st.cache_data
def get_data():
    df = load_data()
    return prepare_data(df)


df = get_data()

st.sidebar.header("Simulation Inputs")

capital = st.sidebar.number_input(
    "Investment amount (€)",
    min_value=0.0,
    value=10000.0,
    step=500.0,
)

available_maturities = sorted(df["Prazo (meses)"].dropna().unique())

maturity_months = st.sidebar.selectbox(
    "Term",
    available_maturities,
    index=available_maturities.index(12) if 12 in available_maturities else 0,
    format_func=lambda x: f"{int(x)} months",
)

available_banks = ["All banks"] + sorted(df["Banco"].dropna().unique())

selected_bank = st.sidebar.selectbox(
    "Bank",
    available_banks,
)

require_early_withdrawal = st.sidebar.checkbox(
    "Require early withdrawal",
    value=False,
)

accept_new_clients_only = st.sidebar.checkbox(
    "Include new-client offers",
    value=True,
)

accept_new_money_only = st.sidebar.checkbox(
    "Include new-money offers",
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
    selected_bank=selected_bank,
    require_early_withdrawal=require_early_withdrawal,
    accept_new_clients_only=accept_new_clients_only,
    accept_new_money_only=accept_new_money_only,
    top_n=top_n,
)

st.subheader("Simulation Summary")

summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

summary_col1.metric("Capital", f"{capital:,.2f} €")
summary_col2.metric("Term", f"{int(maturity_months)} months")
summary_col3.metric("Bank", selected_bank)
summary_col4.metric("Results", top_n)

summary_col5, summary_col6, summary_col7 = st.columns(3)

summary_col5.metric(
    "Early withdrawal required",
    "Yes" if require_early_withdrawal else "No",
)

summary_col6.metric(
    "New-client offers included",
    "Yes" if accept_new_clients_only else "No",
)

summary_col7.metric(
    "New-money offers included",
    "Yes" if accept_new_money_only else "No",
)

if ranking.empty:
    st.info("No eligible deposits found for the selected criteria.")
else:
    best = ranking.iloc[0]

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

    st.markdown(
        f"""
        <div class="simulation-card">
            <div class="card-title">{selected["Banco"]} — {selected["Produto"]}</div>
            <div class="small-muted">Selected product simulation based on the chosen criteria.</div>
            <br>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px;">
                <div>
                    <div class="card-label">Capital invested</div>
                    <div class="card-value">{capital:,.2f} €</div>
                </div>
                <div>
                    <div class="card-label">Term</div>
                    <div class="card-value">{int(selected["Prazo (meses)"])} months</div>
                </div>
                <div>
                    <div class="card-label">TANB</div>
                    <div class="card-value">{selected["TANB (%)"]:.2f}%</div>
                </div>
                <div>
                    <div class="card-label">Final amount</div>
                    <div class="card-value">{selected["Montante final estimado (€)"]:.2f} €</div>
                </div>
                <div>
                    <div class="card-label">Gross interest</div>
                    <div class="card-value">{selected["Juro bruto estimado (€)"]:.2f} €</div>
                </div>
                <div>
                    <div class="card-label">Estimated tax</div>
                    <div class="card-value">{selected["IRS estimado (€)"]:.2f} €</div>
                </div>
                <div>
                    <div class="card-label">Net interest</div>
                    <div class="card-value">{selected["Juro líquido estimado (€)"]:.2f} €</div>
                </div>
                <div>
                    <div class="card-label">Alerts</div>
                    <div class="card-value" style="font-size: 15px;">{selected["Alertas"]}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

    st.subheader("Ranking Results")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Best Bank", best["Banco"])
    col2.metric("Best TANB", f'{best["TANB (%)"]:.2f}%')
    col3.metric("Best Net Interest", f'{best["Juro líquido estimado (€)"]:.2f} €')
    col4.metric("Best Final Amount", f'{best["Montante final estimado (€)"]:.2f} €')

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

    fig = px.bar(
        chart_data.sort_values("Juro líquido estimado (€)", ascending=True),
        x="Juro líquido estimado (€)",
        y="Deposit",
        orientation="h",
        text="Juro líquido estimado (€)",
        labels={
            "Juro líquido estimado (€)": "Estimated net interest (€)",
            "Deposit": "Deposit",
        },
    )

    fig.update_traces(texttemplate="%{text:.2f} €", textposition="outside")
    fig.update_layout(
        height=max(350, 70 * len(chart_data)),
        margin=dict(l=20, r=40, t=20, b=20),
        yaxis_title=None,
        xaxis_title="Estimated net interest (€)",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)

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

    st.subheader("Downloads")

    csv = ranking.to_csv(index=False).encode("utf-8-sig")

    excel_buffer = BytesIO()

    ranking.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    download_col1, download_col2 = st.columns(2)

    download_col1.download_button(
        label="Download ranking as CSV",
        data=csv,
        file_name="ranking_output.csv",
        mime="text/csv",
        use_container_width=True,
    )

    download_col2.download_button(
        label="Download ranking as Excel",
        data=excel_buffer,
        file_name="ranking_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

st.caption(
    "Prototype built with Python, pandas, Plotly and Streamlit. Dataset is manually curated and may not reflect real-time product changes."
)
