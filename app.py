from io import BytesIO
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.calculator import load_data, prepare_data, compare_deposits


# ------------------------------------------------------------
# Paths and links
# ------------------------------------------------------------

METADATA_PATH = Path("data/metadata.json")

GITHUB_URL = "https://github.com/ricardoserodio/portugal-term-deposit-comparator"
LIVE_APP_URL = "https://pt-deposit-comparator.streamlit.app"


# ------------------------------------------------------------
# Interface translations
# ------------------------------------------------------------

TEXT = {
    "en": {
        "language": "Language",
        "simulation_inputs": "Simulation Inputs",
        "app_mode": "App mode",
        "simple": "Simple",
        "advanced": "Advanced",
        "capital_to_invest": "Capital to invest (€)",
        "maturity_months": "Maturity (months)",
        "bank": "Bank",
        "all_banks": "All banks",
        "advanced_filters": "Advanced Filters",
        "require_early_withdrawal": "Require early withdrawal option",
        "accept_new_clients_only": "Accept products for new clients only",
        "accept_new_money_only": "Accept products for new money only",
        "show_only_clean": "Show only products without relevant alerts",
        "number_results": "Number of results",

        "title": "🏦 Portugal Term Deposit Comparator",
        "subtitle": "Compare Portuguese term deposits by estimated net yield, maturity, eligibility criteria and liquidity conditions.",

        "overview": "Overview",
        "simulator": "Simulator",
        "validation": "Validation",
        "details": "Details",

        "dataset_reference_date": "Dataset Reference Date",
        "last_manual_validation": "Last Manual Validation",
        "dataset_status": "Dataset Status",
        "curated_dataset": "Updated with secondary-source review",
        "validation_status": "Validation status",
        "market_scope": "Market scope",
        "data_freshness": "Data freshness",
        "manual_validation_required": "Official source confirmation recommended",

        "project_highlights": "Project Highlights",
        "banking_analytics": "Banking Analytics",
        "banking_analytics_text": "Compares Portuguese term deposits using financial product criteria.",
        "net_yield_simulation": "Net Yield Simulation",
        "net_yield_simulation_text": "Estimates gross interest, tax impact, net interest and final amount.",
        "eligibility_alerts": "Eligibility Alerts",
        "eligibility_alerts_text": "Flags new client rules, new money requirements and liquidity conditions.",
        "human_validation": "Human Validation",
        "human_validation_text": "Uses official source tracking and manual review before dataset updates.",

        "methodology": "Methodology",
        "methodology_intro": "The app follows a simple analytical workflow:",
        "method_1": "Load manually curated term deposit dataset",
        "method_2": "Apply eligibility and liquidity filters",
        "method_3": "Estimate gross interest based on TANB and maturity",
        "method_4": "Estimate tax impact using the selected tax assumption",
        "method_5": "Calculate estimated net interest and final amount",
        "method_6": "Rank deposits by estimated net interest",
        "method_7": "Keep source monitoring separate from manual dataset updates",

        "demonstrates": "What this project demonstrates",
        "demo_1": "Banking product analysis",
        "demo_2": "Python data analysis",
        "demo_3": "Streamlit app development",
        "demo_4": "Financial calculation logic",
        "demo_5": "Data quality awareness",
        "demo_6": "Human-in-the-loop validation",

        "data_quality": "Data Quality & Human Validation",
        "data_quality_dashboard": "Data Quality Dashboard",
        "data_quality_intro": "This section summarizes the dataset governance and validation status used by this tool.",
        "data_quality_note": "The app uses a manually curated dataset and does **not** automatically update deposit rates or product conditions without human review.",
        "human_reviewed": "Human-reviewed",
        "official_source_tracking": "Official Source Tracking",
        "official_source_tracking_text": "Product sources are tracked through `data/source_links.csv`.",
        "human_validation_workflow": "Human Validation Workflow",
        "human_validation_workflow_text": "Source checks generate validation reports before any dataset update.",
        "workflow_expander": "How the validation workflow works",
        "dataset_language_note": "Product notes, alerts and official source comments may remain in Portuguese because they reflect the original dataset and bank documentation.",

        "products_reviewed": "Products reviewed",
        "products_in_simulation": "Products in simulation",
        "products_with_source": "Products with source",
        "products_with_alerts": "Products with alerts",
        "official_validation": "Official validation",
        "pending_where_applicable": "Pending where applicable",
        "validation_status_column": "Validation Status",
        "official_source_validated": "Official source validated",
        "official_confirmation_recommended": "Official confirmation recommended",
        "secondary_source_review": "Secondary-source review",
        "review_required": "Review required",
        "source_coverage_by_bank": "Source Coverage by Bank",
        "validation_status_distribution": "Validation Status Distribution",

        "simulation_summary": "Simulation Summary",
        "capital": "Capital",
        "eligible_results": "Eligible Results",
        "best_net_interest": "Best Net Interest",
        "average_net_interest": "Average Net Interest",
        "maturity": "Maturity",
        "bank_filter": "Bank Filter",
        "best_tanb": "Best TANB",
        "mode": "Mode",

        "recommended_option": "Highest estimated net interest",
        "recommended_reason": "Shown by highest estimated net interest among eligible deposits.",
        "eligibility_warning": "Eligibility alert",
        "eligibility_warning_text": "This product may include specific eligibility conditions. Confirm the latest official documentation before making any financial decision.",
        "new_clients_warning": "This product may be restricted to new clients.",
        "new_money_warning": "This product may require new money or new subscription amounts.",
        "early_withdrawal_warning": "Early withdrawal conditions may be limited or subject to penalties.",

        "selected_deposit_simulation": "Selected Deposit Simulation",
        "select_deposit": "Select deposit to simulate",
        "net_interest": "Net interest",
        "estimated_net_interest": "Estimated Net Interest",
        "estimated_final_amount": "Estimated Final Amount",

        "ranking_results": "Ranking Results",
        "ranking_intro": "The main ranking table shows the most relevant fields for comparison. Full product details, notes and sources are available in the expandable section below.",
        "show_full_table": "Show full technical ranking table",

        "net_interest_comparison": "Net Interest Comparison",
        "chart_title": "Estimated Net Interest by Product",
        "deposit_product": "Deposit Product",

        "product_details": "Product Details, Notes and Sources",
        "tanb": "TANB",
        "estimated_gross_interest": "Estimated Gross Interest",
        "estimated_tax": "Estimated Tax",
        "alerts": "Alerts",
        "notes_conditions": "Notes / Conditions",
        "official_source": "Official Source / Reference",

        "downloads": "Downloads",
        "download_csv": "Download ranking as CSV",
        "download_excel": "Download ranking as Excel",

        "no_eligible": "No eligible deposits found for the selected criteria.",
        "no_after_alert_filter": "No deposits found after applying the alert filter.",

        "footer_built": "MVP prototype built with Python, pandas, Streamlit and Plotly.",
        "footer_warning": "Data should always be validated against official bank sources before any financial decision.",
        "live_app": "Live App",
        "github_repo": "GitHub Repository",
        "technical_note": "Technical note",
        "enabled": "Enabled",
        "months": "months",
        "product": "Product",
    },
    "pt": {
        "language": "Idioma",
        "simulation_inputs": "Entradas da Simulação",
        "app_mode": "Modo da app",
        "simple": "Simples",
        "advanced": "Avançado",
        "capital_to_invest": "Capital a investir (€)",
        "maturity_months": "Prazo (meses)",
        "bank": "Banco",
        "all_banks": "Todos os bancos",
        "advanced_filters": "Filtros Avançados",
        "require_early_withdrawal": "Exigir possibilidade de mobilização antecipada",
        "accept_new_clients_only": "Aceitar produtos apenas para novos clientes",
        "accept_new_money_only": "Aceitar produtos apenas para novos montantes",
        "show_only_clean": "Mostrar apenas produtos sem alertas relevantes",
        "number_results": "Número de resultados",

        "title": "🏦 Comparador de Depósitos a Prazo em Portugal",
        "subtitle": "Compare depósitos a prazo em Portugal por rendimento líquido estimado, prazo, critérios de elegibilidade e condições de liquidez.",

        "overview": "Visão Geral",
        "simulator": "Simulador",
        "validation": "Validação",
        "details": "Detalhes",

        "dataset_reference_date": "Data de Referência dos Dados",
        "last_manual_validation": "Última Validação Manual",
        "dataset_status": "Estado do Dataset",
        "curated_dataset": "Atualizado com revisão por fonte secundária",
        "validation_status": "Estado da validação",
        "market_scope": "Âmbito de mercado",
        "data_freshness": "Atualidade dos dados",
        "manual_validation_required": "Confirmação em fonte oficial recomendada",

        "project_highlights": "Destaques do Projeto",
        "banking_analytics": "Análise Bancária",
        "banking_analytics_text": "Compara depósitos a prazo portugueses com base em critérios de produto financeiro.",
        "net_yield_simulation": "Simulação de Rendimento Líquido",
        "net_yield_simulation_text": "Estima juro bruto, impacto fiscal, juro líquido e montante final.",
        "eligibility_alerts": "Alertas de Elegibilidade",
        "eligibility_alerts_text": "Sinaliza regras de novos clientes, novos montantes e condições de liquidez.",
        "human_validation": "Validação Humana",
        "human_validation_text": "Usa acompanhamento de fontes oficiais e revisão manual antes de atualizar dados.",

        "methodology": "Metodologia",
        "methodology_intro": "A app segue um workflow analítico simples:",
        "method_1": "Carregar dataset de depósitos a prazo manualmente curado",
        "method_2": "Aplicar filtros de elegibilidade e liquidez",
        "method_3": "Estimar juro bruto com base na TANB e no prazo",
        "method_4": "Estimar impacto fiscal com base no pressuposto fiscal definido",
        "method_5": "Calcular juro líquido estimado e montante final",
        "method_6": "Ordenar depósitos por juro líquido estimado",
        "method_7": "Manter monitorização de fontes separada das atualizações manuais do dataset",

        "demonstrates": "O que este projeto demonstra",
        "demo_1": "Análise de produto bancário",
        "demo_2": "Análise de dados em Python",
        "demo_3": "Desenvolvimento de app em Streamlit",
        "demo_4": "Lógica de cálculo financeiro",
        "demo_5": "Consciência de qualidade dos dados",
        "demo_6": "Validação humana no processo",

        "data_quality": "Qualidade dos Dados e Validação Humana",
        "data_quality_dashboard": "Dashboard de Qualidade dos Dados",
        "data_quality_intro": "Esta secção resume a governação dos dados e o estado de validação usado por esta ferramenta.",
        "data_quality_note": "A app usa um dataset manualmente curado e **não** atualiza automaticamente taxas ou condições dos produtos sem revisão humana.",
        "human_reviewed": "Revisto humanamente",
        "official_source_tracking": "Acompanhamento de Fontes Oficiais",
        "official_source_tracking_text": "As fontes dos produtos são acompanhadas através de `data/source_links.csv`.",
        "human_validation_workflow": "Workflow de Validação Humana",
        "human_validation_workflow_text": "As verificações de fontes geram relatórios de validação antes de qualquer atualização do dataset.",
        "workflow_expander": "Como funciona o workflow de validação",
        "dataset_language_note": "As notas dos produtos, alertas e comentários de fontes podem permanecer em português por refletirem o dataset original e a documentação bancária.",

        "products_reviewed": "Produtos revistos",
        "products_in_simulation": "Produtos na simulação",
        "products_with_source": "Produtos com fonte",
        "products_with_alerts": "Produtos com alertas",
        "official_validation": "Validação oficial",
        "pending_where_applicable": "Pendente quando aplicável",
        "validation_status_column": "Estado de Validação",
        "official_source_validated": "Fonte oficial validada",
        "official_confirmation_recommended": "Confirmação oficial recomendada",
        "secondary_source_review": "Revisão por fonte secundária",
        "review_required": "Revisão necessária",
        "source_coverage_by_bank": "Cobertura de Fontes por Banco",
        "validation_status_distribution": "Distribuição do Estado de Validação",

        "simulation_summary": "Resumo da Simulação",
        "capital": "Capital",
        "eligible_results": "Resultados Elegíveis",
        "best_net_interest": "Melhor Juro Líquido",
        "average_net_interest": "Juro Líquido Médio",
        "maturity": "Prazo",
        "bank_filter": "Filtro de Banco",
        "best_tanb": "Melhor TANB",
        "mode": "Modo",

        "recommended_option": "Maior juro líquido estimado",
        "recommended_reason": "Apresentado por maior juro líquido estimado entre os depósitos elegíveis.",
        "eligibility_warning": "Alerta de elegibilidade",
        "eligibility_warning_text": "Este produto pode incluir condições específicas de elegibilidade. Confirme sempre a documentação oficial mais recente antes de qualquer decisão financeira.",
        "new_clients_warning": "Este produto pode estar limitado a novos clientes.",
        "new_money_warning": "Este produto pode exigir novos montantes ou novas subscrições.",
        "early_withdrawal_warning": "As condições de mobilização antecipada podem ser limitadas ou sujeitas a penalizações.",

        "selected_deposit_simulation": "Simulação do Depósito Selecionado",
        "select_deposit": "Selecionar depósito para simular",
        "net_interest": "Juro líquido",
        "estimated_net_interest": "Juro Líquido Estimado",
        "estimated_final_amount": "Montante Final Estimado",

        "ranking_results": "Resultados do Ranking",
        "ranking_intro": "A tabela principal mostra os campos mais relevantes para comparação. Os detalhes completos, notas e fontes estão disponíveis na secção expansível abaixo.",
        "show_full_table": "Mostrar tabela técnica completa",

        "net_interest_comparison": "Comparação de Juro Líquido",
        "chart_title": "Juro Líquido Estimado por Produto",
        "deposit_product": "Produto de Depósito",

        "product_details": "Detalhes dos Produtos, Notas e Fontes",
        "tanb": "TANB",
        "estimated_gross_interest": "Juro Bruto Estimado",
        "estimated_tax": "Imposto Estimado",
        "alerts": "Alertas",
        "notes_conditions": "Notas / Condições",
        "official_source": "Fonte Oficial / Referência",

        "downloads": "Descarregamentos",
        "download_csv": "Descarregar ranking em CSV",
        "download_excel": "Descarregar ranking em Excel",

        "no_eligible": "Não foram encontrados depósitos elegíveis para os critérios selecionados.",
        "no_after_alert_filter": "Não foram encontrados depósitos após aplicar o filtro de alertas.",

        "footer_built": "Protótipo MVP criado com Python, pandas, Streamlit e Plotly.",
        "footer_warning": "Os dados devem ser sempre validados contra fontes oficiais dos bancos antes de qualquer decisão financeira.",
        "live_app": "App online",
        "github_repo": "Repositório GitHub",
        "technical_note": "Nota técnica",
        "enabled": "Ativo",
        "months": "meses",
        "product": "Produto",
    },
}


# ------------------------------------------------------------
# Translation helpers
# ------------------------------------------------------------

def get_language_code(language_label: str) -> str:
    return "pt" if language_label == "Português" else "en"


def translate(lang: str, key: str) -> str:
    return TEXT.get(lang, TEXT["en"]).get(key, key)


# ------------------------------------------------------------
# Metadata loader
# ------------------------------------------------------------

def load_metadata(path: Path = METADATA_PATH) -> dict:
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
    for col in candidates:
        if col in df.columns:
            return col
    return None


def get_series_value(row: pd.Series, column_name: str | None, default: str = "N/A"):
    if column_name and column_name in row.index:
        return row[column_name]
    return default


def has_value(value) -> bool:
    if pd.isna(value):
        return False

    text = str(value).strip().lower()

    empty_values = [
        "",
        "n/a",
        "na",
        "nan",
        "none",
        "not available",
        "não disponível",
        "nao disponivel",
    ]

    return text not in empty_values


def is_affirmative(value) -> bool:
    if pd.isna(value):
        return False

    text = str(value).strip().lower()

    affirmative_values = [
        "yes",
        "y",
        "sim",
        "true",
        "1",
        "required",
        "obrigatório",
        "obrigatorio",
        "exclusive",
        "exclusivo",
        "only",
        "apenas",
    ]

    return any(token in text for token in affirmative_values)


def is_negative(value) -> bool:
    if pd.isna(value):
        return False

    text = str(value).strip().lower()

    negative_values = [
        "no",
        "não",
        "nao",
        "false",
        "0",
        "not",
        "sem",
        "not required",
        "não obrigatório",
        "nao obrigatorio",
    ]

    return any(token in text for token in negative_values)


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Ranking")

    return output.getvalue()


def format_currency(value) -> str:
    try:
        return f"{float(value):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "N/A"


def format_percentage(value) -> str:
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return "N/A"


def truncate_text(value, max_length: int = 60) -> str:
    text = str(value)
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def is_clean_alert(value) -> bool:
    if pd.isna(value):
        return True

    text = str(value).strip().lower()

    clean_values = [
        "",
        "no alerts",
        "sem alertas",
        "none",
        "n/a",
        "nan",
    ]

    return text in clean_values


def infer_validation_status(
    row: pd.Series,
    lang: str,
    source_col: str | None,
    alerts_col: str | None,
) -> str:
    source_value = get_series_value(row, source_col, "") if source_col else ""
    alerts_value = get_series_value(row, alerts_col, "") if alerts_col else ""

    if has_value(source_value) and is_clean_alert(alerts_value):
        return translate(lang, "official_source_validated")

    if has_value(source_value):
        return translate(lang, "official_confirmation_recommended")

    if not has_value(source_value) and has_value(alerts_value):
        return translate(lang, "review_required")

    return translate(lang, "secondary_source_review")


def build_clean_ranking_table(
    ranking: pd.DataFrame,
    lang: str,
    bank_col: str | None,
    product_col: str | None,
    maturity_col: str | None,
    tanb_col: str | None,
    net_interest_col: str | None,
    final_amount_col: str | None,
    alerts_col: str | None,
    source_col: str | None,
) -> pd.DataFrame:
    display_df = pd.DataFrame()

    if bank_col:
        display_df[translate(lang, "bank")] = ranking[bank_col]

    if product_col:
        display_df[translate(lang, "product")] = ranking[product_col]

    if maturity_col:
        display_df[translate(lang, "maturity")] = (
            ranking[maturity_col].astype(str) + f" {translate(lang, 'months')}"
        )

    if tanb_col:
        display_df["TANB"] = ranking[tanb_col].apply(format_percentage)

    if net_interest_col:
        display_df[translate(lang, "estimated_net_interest")] = ranking[net_interest_col].apply(format_currency)

    if final_amount_col:
        display_df[translate(lang, "estimated_final_amount")] = ranking[final_amount_col].apply(format_currency)

    display_df[translate(lang, "validation_status_column")] = ranking.apply(
        lambda row: infer_validation_status(
            row=row,
            lang=lang,
            source_col=source_col,
            alerts_col=alerts_col,
        ),
        axis=1,
    )

    if alerts_col:
        display_df[translate(lang, "alerts")] = ranking[alerts_col]

    return display_df


def build_eligibility_warnings(
    row: pd.Series,
    lang: str,
    new_clients_col: str | None,
    new_money_col: str | None,
    early_withdrawal_col: str | None,
) -> list[str]:
    warnings = []

    new_clients_value = get_series_value(row, new_clients_col, "") if new_clients_col else ""
    new_money_value = get_series_value(row, new_money_col, "") if new_money_col else ""
    early_withdrawal_value = get_series_value(row, early_withdrawal_col, "") if early_withdrawal_col else ""

    if is_affirmative(new_clients_value):
        warnings.append(translate(lang, "new_clients_warning"))

    if is_affirmative(new_money_value):
        warnings.append(translate(lang, "new_money_warning"))

    if early_withdrawal_col and (is_negative(early_withdrawal_value) or not has_value(early_withdrawal_value)):
        warnings.append(translate(lang, "early_withdrawal_warning"))

    return warnings


def get_source_coverage_dataframe(
    df: pd.DataFrame,
    bank_col: str | None,
    source_col: str | None,
) -> pd.DataFrame:
    if not bank_col:
        return pd.DataFrame()

    temp_df = df.copy()

    if source_col:
        temp_df["Has Source"] = temp_df[source_col].apply(has_value)
    else:
        temp_df["Has Source"] = False

    coverage = (
        temp_df.groupby(bank_col, dropna=False)
        .agg(
            Products=(bank_col, "size"),
            Products_With_Source=("Has Source", "sum"),
        )
        .reset_index()
    )

    coverage["Source_Coverage_%"] = (
        coverage["Products_With_Source"] / coverage["Products"] * 100
    ).round(1)

    return coverage.rename(columns={bank_col: "Bank"})


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
    /* Global dark theme */
    .stApp {
        background-color: #020617 !important;
        color: #F9FAFB !important;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #020617 !important;
        color: #F9FAFB !important;
    }

    [data-testid="stMain"] {
        background-color: #020617 !important;
        color: #F9FAFB !important;
    }

    [data-testid="stMainBlockContainer"] {
        background-color: #020617 !important;
        color: #F9FAFB !important;
    }

    /* Header / top bar */
    [data-testid="stHeader"] {
        background-color: #020617 !important;
        color: #F9FAFB !important;
    }

    header {
        background-color: #020617 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        color: #F9FAFB !important;
    }

    [data-testid="stSidebarContent"] {
        background-color: #0F172A !important;
        color: #F9FAFB !important;
    }

    [data-testid="stSidebar"] * {
        color: #F9FAFB !important;
    }

    /* Sidebar input containers */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] select {
        background-color: #111827 !important;
        color: #F9FAFB !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] label {
        color: #F9FAFB !important;
        font-weight: 600 !important;
    }

    /* Selectbox / number input / radio / slider labels */
    [data-testid="stSelectbox"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stSlider"] label,
    [data-testid="stRadio"] label {
        color: #F9FAFB !important;
    }

    /* Radio buttons */
    [role="radiogroup"] label {
        color: #F9FAFB !important;
    }

    /* General headings and text */
    h1, h2, h3, h4, h5, h6 {
        color: #F9FAFB !important;
    }

    p, span, label {
        color: inherit;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: transparent !important;
        color: #F9FAFB !important;
    }

    [data-testid="stMetric"] label {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetric"] div {
        color: #F9FAFB !important;
    }

    [data-testid="stMetricValue"] {
        color: #F9FAFB !important;
    }

    [data-testid="stMetricLabel"] {
        color: #CBD5E1 !important;
    }

    /* Tabs */
    [data-testid="stTabs"] button {
        color: #CBD5E1 !important;
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #F87171 !important;
        font-weight: 700 !important;
    }

    /* Native Streamlit alerts */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
        background-color: #111827 !important;
        color: #F9FAFB !important;
    }

    [data-testid="stAlert"] * {
        color: #F9FAFB !important;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        background-color: #0F172A !important;
        color: #F9FAFB !important;
    }

    /* Custom title */
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
        color: #F9FAFB !important;
    }

    .subtitle {
        font-size: 17px;
        color: #CBD5E1 !important;
        margin-bottom: 25px;
    }

    .small-muted {
        font-size: 13px;
        color: #CBD5E1 !important;
    }

    /* Custom cards */
    .simulation-card {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 24px;
        margin-top: 10px;
        margin-bottom: 20px;
        color: #F9FAFB;
    }

    .recommended-card {
        background-color: #052E16;
        border: 1px solid #16A34A;
        border-radius: 16px;
        padding: 20px;
        margin-top: 10px;
        margin-bottom: 20px;
        color: #F9FAFB;
    }

    .warning-card {
        background-color: #422006;
        border: 1px solid #F59E0B;
        border-radius: 16px;
        padding: 18px;
        margin-top: 10px;
        margin-bottom: 20px;
        color: #FFFFFF;
    }

    .freshness-card {
        background-color: #422006;
        border: 1px solid #F59E0B;
        border-radius: 16px;
        padding: 18px;
        margin-top: 10px;
        margin-bottom: 20px;
        color: #FFFFFF;
    }

    .freshness-card .card-title,
    .freshness-card .card-line,
    .warning-card .card-title,
    .warning-card .card-line {
        color: #FFFFFF !important;
    }

    .card-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 10px;
        color: #F9FAFB !important;
    }

    .card-line {
        font-size: 15px;
        margin-bottom: 6px;
        color: #F9FAFB !important;
    }

    .highlight-card {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        min-height: 155px;
        margin-bottom: 10px;
        color: #F9FAFB;
    }

    .highlight-icon {
        font-size: 26px;
        margin-bottom: 8px;
        color: #F9FAFB !important;
    }

    .highlight-title {
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 8px;
        color: #F9FAFB !important;
    }

    .highlight-text {
        font-size: 14px;
        color: #E5E7EB !important;
        line-height: 1.45;
    }

    .footer-box {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 16px;
        margin-top: 20px;
        color: #F9FAFB;
    }

    .footer-box .small-muted {
        color: #CBD5E1 !important;
    }

    a {
        text-decoration: none;
        color: #60A5FA !important;
    }

    a:hover {
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------

metadata = load_metadata()

df = load_data()
df = prepare_data(df)


# ------------------------------------------------------------
# Sidebar inputs
# ------------------------------------------------------------

language_label = st.sidebar.selectbox(
    "Language / Idioma",
    options=["English", "Português"],
    index=0,
)

lang = get_language_code(language_label)

st.sidebar.header(translate(lang, "simulation_inputs"))

app_mode_label = st.sidebar.radio(
    translate(lang, "app_mode"),
    options=[translate(lang, "simple"), translate(lang, "advanced")],
    index=0,
)

is_advanced_mode = app_mode_label == translate(lang, "advanced")

capital = st.sidebar.number_input(
    translate(lang, "capital_to_invest"),
    min_value=0.0,
    value=10000.0,
    step=500.0,
    format="%.2f",
)

maturity_col = find_column(df, ["Prazo (meses)", "Maturity", "Maturity (months)"])
bank_col = find_column(df, ["Banco", "Bank"])

source_col_df = find_column(
    df,
    [
        "Fonte oficial / referência",
        "Fonte oficial",
        "Official source",
        "Source",
        "Reference",
    ],
)

alerts_col_df = find_column(df, ["Alertas", "Alerts"])

if maturity_col:
    available_maturities = sorted(df[maturity_col].dropna().unique())
else:
    available_maturities = [3, 6, 12, 24]

maturity_months = st.sidebar.selectbox(
    translate(lang, "maturity_months"),
    options=available_maturities,
    index=available_maturities.index(12) if 12 in available_maturities else 0,
)

if bank_col:
    original_banks = sorted(df[bank_col].dropna().astype(str).unique().tolist())
    available_banks_display = [translate(lang, "all_banks")] + original_banks
else:
    available_banks_display = [translate(lang, "all_banks")]

selected_bank_display = st.sidebar.selectbox(
    translate(lang, "bank"),
    options=available_banks_display,
)

selected_bank = "All banks" if selected_bank_display == translate(lang, "all_banks") else selected_bank_display

if is_advanced_mode:
    st.sidebar.subheader(translate(lang, "advanced_filters"))

    require_early_withdrawal = st.sidebar.checkbox(
        translate(lang, "require_early_withdrawal"),
        value=False,
    )

    accept_new_clients_only = st.sidebar.checkbox(
        translate(lang, "accept_new_clients_only"),
        value=True,
    )

    accept_new_money_only = st.sidebar.checkbox(
        translate(lang, "accept_new_money_only"),
        value=True,
    )

    show_only_without_relevant_alerts = st.sidebar.checkbox(
        translate(lang, "show_only_clean"),
        value=False,
    )

else:
    require_early_withdrawal = False
    accept_new_clients_only = True
    accept_new_money_only = True
    show_only_without_relevant_alerts = False

top_n = st.sidebar.slider(
    translate(lang, "number_results"),
    min_value=3,
    max_value=20,
    value=10,
)


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.markdown(
    f'<div class="main-title">{translate(lang, "title")}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="subtitle">{translate(lang, "subtitle")}</div>',
    unsafe_allow_html=True,
)


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

if ranking is None or ranking.empty:
    st.error(translate(lang, "no_eligible"))
    st.stop()


# ------------------------------------------------------------
# Column detection
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

new_clients_col = find_column(
    ranking,
    [
        "Novos clientes",
        "Novo cliente",
        "New clients",
        "New client",
        "Only new clients",
    ],
)

new_money_col = find_column(
    ranking,
    [
        "Novos montantes",
        "Novo montante",
        "New money",
        "New amounts",
        "Only new money",
    ],
)

early_withdrawal_col = find_column(
    ranking,
    [
        "Mobilização antecipada",
        "Mobilizacao antecipada",
        "Early withdrawal",
        "Withdrawable",
        "Mobil/Internet",
    ],
)


# ------------------------------------------------------------
# Optional alert filtering
# ------------------------------------------------------------

if show_only_without_relevant_alerts and alerts_col:
    ranking = ranking[ranking[alerts_col].apply(is_clean_alert)].copy()

if ranking.empty:
    st.error(translate(lang, "no_after_alert_filter"))
    st.stop()


# ------------------------------------------------------------
# Add validation status column to technical ranking
# ------------------------------------------------------------

ranking = ranking.copy()
ranking[translate(lang, "validation_status_column")] = ranking.apply(
    lambda row: infer_validation_status(
        row=row,
        lang=lang,
        source_col=source_col,
        alerts_col=alerts_col,
    ),
    axis=1,
)


# ------------------------------------------------------------
# Tabs
# ------------------------------------------------------------

overview_tab, simulator_tab, validation_tab, details_tab = st.tabs(
    [
        translate(lang, "overview"),
        translate(lang, "simulator"),
        translate(lang, "validation"),
        translate(lang, "details"),
    ]
)


# ------------------------------------------------------------
# Overview tab
# ------------------------------------------------------------

with overview_tab:
    meta_col1, meta_col2, meta_col3 = st.columns(3)

    with meta_col1:
        st.metric(
            label=translate(lang, "dataset_reference_date"),
            value=metadata.get("reference_date", "Not available"),
        )

    with meta_col2:
        st.metric(
            label=translate(lang, "last_manual_validation"),
            value=metadata.get("last_manual_validation", "Not available"),
        )

    with meta_col3:
        st.metric(
            label=translate(lang, "dataset_status"),
            value=translate(lang, "curated_dataset"),
        )

    st.info(
        f"""
        **{translate(lang, "validation_status")}:** {metadata.get("validation_status", "Not available")}  
        **{translate(lang, "market_scope")}:** {metadata.get("market_scope", "Not available")}
        """
    )

    st.markdown(
        f"""
        <div class="freshness-card">
            <div class="card-title">⚠️ {translate(lang, "data_freshness")}</div>
            <div class="card-line"><strong>{translate(lang, "manual_validation_required")}</strong></div>
            <div class="card-line">{metadata.get("real_time_warning", metadata.get("disclaimer", ""))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        metadata.get(
            "disclaimer",
            "This tool is for educational and informational purposes only. It does not constitute financial advice.",
        )
    )

    dq_overview_col1, dq_overview_col2, dq_overview_col3, dq_overview_col4 = st.columns(4)

    source_count = df[source_col_df].apply(has_value).sum() if source_col_df else 0
    alerts_count = df[alerts_col_df].apply(lambda value: not is_clean_alert(value)).sum() if alerts_col_df else 0

    with dq_overview_col1:
        st.metric(translate(lang, "products_reviewed"), len(df))

    with dq_overview_col2:
        st.metric(translate(lang, "products_in_simulation"), len(ranking))

    with dq_overview_col3:
        st.metric(translate(lang, "products_with_source"), int(source_count))

    with dq_overview_col4:
        st.metric(translate(lang, "official_validation"), translate(lang, "pending_where_applicable"))

    st.markdown(f"## {translate(lang, 'project_highlights')}")

    highlight_col1, highlight_col2, highlight_col3, highlight_col4 = st.columns(4)

    with highlight_col1:
        st.markdown(
            f"""
            <div class="highlight-card">
                <div class="highlight-icon">🏦</div>
                <div class="highlight-title">{translate(lang, "banking_analytics")}</div>
                <div class="highlight-text">{translate(lang, "banking_analytics_text")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with highlight_col2:
        st.markdown(
            f"""
            <div class="highlight-card">
                <div class="highlight-icon">📈</div>
                <div class="highlight-title">{translate(lang, "net_yield_simulation")}</div>
                <div class="highlight-text">{translate(lang, "net_yield_simulation_text")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with highlight_col3:
        st.markdown(
            f"""
            <div class="highlight-card">
                <div class="highlight-icon">⚠️</div>
                <div class="highlight-title">{translate(lang, "eligibility_alerts")}</div>
                <div class="highlight-text">{translate(lang, "eligibility_alerts_text")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with highlight_col4:
        st.markdown(
            f"""
            <div class="highlight-card">
                <div class="highlight-icon">✅</div>
                <div class="highlight-title">{translate(lang, "human_validation")}</div>
                <div class="highlight-text">{translate(lang, "human_validation_text")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(f"## {translate(lang, 'methodology')}")
    st.markdown(translate(lang, "methodology_intro"))

    st.markdown(
        f"""
        1. {translate(lang, "method_1")}
        2. {translate(lang, "method_2")}
        3. {translate(lang, "method_3")}
        4. {translate(lang, "method_4")}
        5. {translate(lang, "method_5")}
        6. {translate(lang, "method_6")}
        7. {translate(lang, "method_7")}
        """
    )

    st.markdown(f"## {translate(lang, 'demonstrates')}")

    demo_col1, demo_col2, demo_col3 = st.columns(3)

    with demo_col1:
        st.success(f"✅ {translate(lang, 'demo_1')}")
        st.success(f"✅ {translate(lang, 'demo_2')}")

    with demo_col2:
        st.success(f"✅ {translate(lang, 'demo_3')}")
        st.success(f"✅ {translate(lang, 'demo_4')}")

    with demo_col3:
        st.success(f"✅ {translate(lang, 'demo_5')}")
        st.success(f"✅ {translate(lang, 'demo_6')}")


# ------------------------------------------------------------
# Simulator tab
# ------------------------------------------------------------

with simulator_tab:
    st.markdown(f"## {translate(lang, 'simulation_summary')}")

    best_net_interest_value = None
    average_net_interest_value = None
    best_tanb_value = None

    if net_interest_col:
        net_series = pd.to_numeric(ranking[net_interest_col], errors="coerce")
        if not net_series.dropna().empty:
            best_net_interest_value = net_series.max()
            average_net_interest_value = net_series.mean()
            recommended_index = net_series.idxmax()
        else:
            recommended_index = ranking.index[0]
    else:
        recommended_index = ranking.index[0]

    if tanb_col_r:
        tanb_series = pd.to_numeric(ranking[tanb_col_r], errors="coerce")
        if not tanb_series.dropna().empty:
            best_tanb_value = tanb_series.max()

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

    with summary_col1:
        st.metric(translate(lang, "capital"), format_currency(capital))

    with summary_col2:
        st.metric(translate(lang, "eligible_results"), len(ranking))

    with summary_col3:
        st.metric(
            translate(lang, "best_net_interest"),
            format_currency(best_net_interest_value) if best_net_interest_value is not None else "N/A",
        )

    with summary_col4:
        st.metric(
            translate(lang, "average_net_interest"),
            format_currency(average_net_interest_value) if average_net_interest_value is not None else "N/A",
        )

    summary_col5, summary_col6, summary_col7, summary_col8 = st.columns(4)

    with summary_col5:
        st.metric(translate(lang, "maturity"), f"{maturity_months} {translate(lang, 'months')}")

    with summary_col6:
        st.metric(translate(lang, "bank_filter"), selected_bank_display)

    with summary_col7:
        st.metric(
            translate(lang, "best_tanb"),
            format_percentage(best_tanb_value) if best_tanb_value is not None else "N/A",
        )

    with summary_col8:
        st.metric(translate(lang, "mode"), app_mode_label)

    best_row = ranking.loc[recommended_index]
    best_bank = get_series_value(best_row, bank_col_r)
    best_product = get_series_value(best_row, product_col_r)
    best_net = get_series_value(best_row, net_interest_col)

    st.markdown(
        f"""
        <div class="recommended-card">
            <div class="card-title">✅ {translate(lang, "recommended_option")}</div>
            <div class="card-line"><strong>{best_bank} — {best_product}</strong></div>
            <div class="card-line">{translate(lang, "recommended_reason")}</div>
            <div class="card-line"><strong>{translate(lang, "estimated_net_interest")}:</strong> {format_currency(best_net)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    best_eligibility_warnings = build_eligibility_warnings(
        row=best_row,
        lang=lang,
        new_clients_col=new_clients_col,
        new_money_col=new_money_col,
        early_withdrawal_col=early_withdrawal_col,
    )

    if best_eligibility_warnings:
        warning_lines = "".join(
            f'<div class="card-line">• {warning}</div>'
            for warning in best_eligibility_warnings
        )

        st.markdown(
            f"""
            <div class="warning-card">
                <div class="card-title">⚠️ {translate(lang, "eligibility_warning")}</div>
                <div class="card-line">{translate(lang, "eligibility_warning_text")}</div>
                {warning_lines}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(f"## {translate(lang, 'selected_deposit_simulation')}")

    selection_df = ranking.copy().reset_index(drop=True)

    def build_deposit_label(row: pd.Series) -> str:
        bank_name = get_series_value(row, bank_col_r)
        product_name = get_series_value(row, product_col_r)
        tanb_value = format_percentage(get_series_value(row, tanb_col_r)) if tanb_col_r else "N/A"
        net_value = format_currency(get_series_value(row, net_interest_col)) if net_interest_col else "N/A"

        return f"{bank_name} — {product_name} | TANB {tanb_value} | {translate(lang, 'net_interest')} {net_value}"

    selection_df["Deposit Selection Label"] = selection_df.apply(build_deposit_label, axis=1)

    selected_label = st.selectbox(
        translate(lang, "select_deposit"),
        options=selection_df["Deposit Selection Label"].tolist(),
        index=0,
    )

    selected_index = selection_df.index[
        selection_df["Deposit Selection Label"] == selected_label
    ][0]

    selected_deposit = selection_df.iloc[selected_index]

    selected_bank_name = get_series_value(selected_deposit, bank_col_r)
    selected_product_name = get_series_value(selected_deposit, product_col_r)
    selected_tanb = get_series_value(selected_deposit, tanb_col_r)
    selected_net_interest = get_series_value(selected_deposit, net_interest_col)
    selected_final_amount = get_series_value(selected_deposit, final_amount_col)

    st.markdown(
        f"""
        <div class="simulation-card">
            <div class="card-title">{selected_bank_name} — {selected_product_name}</div>
            <div class="card-line"><strong>{translate(lang, "capital")}:</strong> {format_currency(capital)}</div>
            <div class="card-line"><strong>{translate(lang, "maturity")}:</strong> {maturity_months} {translate(lang, "months")}</div>
            <div class="card-line"><strong>TANB:</strong> {format_percentage(selected_tanb)}</div>
            <div class="card-line"><strong>{translate(lang, "estimated_net_interest")}:</strong> {format_currency(selected_net_interest)}</div>
            <div class="card-line"><strong>{translate(lang, "estimated_final_amount")}:</strong> {format_currency(selected_final_amount)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_eligibility_warnings = build_eligibility_warnings(
        row=selected_deposit,
        lang=lang,
        new_clients_col=new_clients_col,
        new_money_col=new_money_col,
        early_withdrawal_col=early_withdrawal_col,
    )

    if selected_eligibility_warnings:
        selected_warning_lines = "\n".join(
            f"- {warning}"
            for warning in selected_eligibility_warnings
        )

        st.warning(
            f"**{translate(lang, 'eligibility_warning')}:**\n\n{selected_warning_lines}"
        )

    st.markdown(f"## {translate(lang, 'ranking_results')}")
    st.markdown(translate(lang, "ranking_intro"))

    clean_ranking_display = build_clean_ranking_table(
        ranking=ranking,
        lang=lang,
        bank_col=bank_col_r,
        product_col=product_col_r,
        maturity_col=maturity_col_r,
        tanb_col=tanb_col_r,
        net_interest_col=net_interest_col,
        final_amount_col=final_amount_col,
        alerts_col=alerts_col,
        source_col=source_col,
    )

    st.dataframe(
        clean_ranking_display,
        use_container_width=True,
        hide_index=True,
    )

    with st.expander(translate(lang, "show_full_table")):
        st.dataframe(
            ranking,
            use_container_width=True,
            hide_index=True,
        )

    if net_interest_col and product_col_r:
        st.markdown(f"## {translate(lang, 'net_interest_comparison')}")

        chart_df = ranking.copy()

        if bank_col_r:
            chart_df["Display Label"] = (
                chart_df[bank_col_r].astype(str)
                + " — "
                + chart_df[product_col_r].astype(str)
            )
        else:
            chart_df["Display Label"] = chart_df[product_col_r].astype(str)

        chart_df["Short Label"] = chart_df["Display Label"].apply(lambda x: truncate_text(x, 55))
        chart_df = chart_df.sort_values(net_interest_col, ascending=True)

        hover_data = ["Display Label"]

        if tanb_col_r:
            hover_data.append(tanb_col_r)

        if final_amount_col:
            hover_data.append(final_amount_col)

        if alerts_col:
            hover_data.append(alerts_col)

        fig = px.bar(
            chart_df,
            x=net_interest_col,
            y="Short Label",
            orientation="h",
            title=translate(lang, "chart_title"),
            labels={
                net_interest_col: translate(lang, "estimated_net_interest"),
                "Short Label": translate(lang, "deposit_product"),
            },
            hover_data=hover_data,
            text=net_interest_col,
        )

        fig.update_traces(
            texttemplate="%{x:.2f} €",
            textposition="outside",
            cliponaxis=False,
        )

        fig.update_layout(
            height=max(420, len(chart_df) * 55),
            showlegend=False,
            margin=dict(l=20, r=90, t=60, b=20),
        )

        st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------
# Validation tab
# ------------------------------------------------------------

with validation_tab:
    st.markdown(f"## {translate(lang, 'data_quality')}")

    st.markdown(
        f"""
        {translate(lang, "data_quality_intro")}

        {translate(lang, "data_quality_note")}
        """
    )

    dq_col1, dq_col2, dq_col3, dq_col4 = st.columns(4)

    source_count = df[source_col_df].apply(has_value).sum() if source_col_df else 0
    alerts_count = df[alerts_col_df].apply(lambda value: not is_clean_alert(value)).sum() if alerts_col_df else 0

    with dq_col1:
        st.metric(
            label=translate(lang, "products_reviewed"),
            value=len(df),
        )

    with dq_col2:
        st.metric(
            label=translate(lang, "products_in_simulation"),
            value=len(ranking),
        )

    with dq_col3:
        st.metric(
            label=translate(lang, "products_with_source"),
            value=int(source_count),
        )

    with dq_col4:
        st.metric(
            label=translate(lang, "products_with_alerts"),
            value=int(alerts_count),
        )

    dq_col5, dq_col6 = st.columns(2)

    with dq_col5:
        st.info(
            f"""
            **{translate(lang, "official_source_tracking")}:** {translate(lang, "enabled")}  
            {translate(lang, "official_source_tracking_text")}
            """
        )

    with dq_col6:
        st.success(
            f"""
            **{translate(lang, "human_validation_workflow")}:** {translate(lang, "enabled")}  
            {translate(lang, "human_validation_workflow_text")}
            """
        )

    st.markdown(f"## {translate(lang, 'data_quality_dashboard')}")

    validation_status_df = ranking[translate(lang, "validation_status_column")].value_counts().reset_index()
    validation_status_df.columns = [translate(lang, "validation_status_column"), "Count"]

    if not validation_status_df.empty:
        fig_validation = px.bar(
            validation_status_df,
            x=translate(lang, "validation_status_column"),
            y="Count",
            title=translate(lang, "validation_status_distribution"),
            text="Count",
        )

        fig_validation.update_traces(textposition="outside", cliponaxis=False)
        fig_validation.update_layout(showlegend=False)

        st.plotly_chart(fig_validation, use_container_width=True)

    source_coverage_df = get_source_coverage_dataframe(
        df=df,
        bank_col=bank_col,
        source_col=source_col_df,
    )

    if not source_coverage_df.empty:
        st.markdown(f"### {translate(lang, 'source_coverage_by_bank')}")

        st.dataframe(
            source_coverage_df,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(f"**{translate(lang, 'technical_note')}:** {translate(lang, 'dataset_language_note')}")

    with st.expander(translate(lang, "workflow_expander")):
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

            ```bash
            scripts/monitor_sources.py
            ```

            ```bash
            data/source_links.csv
            ```

            ```bash
            validation/
            ```
            """
        )


# ------------------------------------------------------------
# Details tab
# ------------------------------------------------------------

with details_tab:
    st.markdown(f"## {translate(lang, 'product_details')}")

    st.caption(f"**{translate(lang, 'technical_note')}:** {translate(lang, 'dataset_language_note')}")

    for _, row in ranking.iterrows():
        bank_name = get_series_value(row, bank_col_r)
        product_name = get_series_value(row, product_col_r)

        with st.expander(f"{bank_name} — {product_name}"):
            detail_col1, detail_col2, detail_col3 = st.columns(3)

            with detail_col1:
                if tanb_col_r:
                    st.metric("TANB", format_percentage(get_series_value(row, tanb_col_r)))

                if maturity_col_r:
                    st.write(
                        f"**{translate(lang, 'maturity')}:** "
                        f"{get_series_value(row, maturity_col_r)} {translate(lang, 'months')}"
                    )

            with detail_col2:
                if gross_interest_col:
                    st.metric(
                        translate(lang, "estimated_gross_interest"),
                        format_currency(get_series_value(row, gross_interest_col)),
                    )

                if tax_col:
                    st.metric(
                        translate(lang, "estimated_tax"),
                        format_currency(get_series_value(row, tax_col)),
                    )

            with detail_col3:
                if net_interest_col:
                    st.metric(
                        translate(lang, "estimated_net_interest"),
                        format_currency(get_series_value(row, net_interest_col)),
                    )

                if final_amount_col:
                    st.metric(
                        translate(lang, "estimated_final_amount"),
                        format_currency(get_series_value(row, final_amount_col)),
                    )

            st.write(
                f"**{translate(lang, 'validation_status_column')}:** "
                f"{infer_validation_status(row, lang, source_col, alerts_col)}"
            )

            product_warnings = build_eligibility_warnings(
                row=row,
                lang=lang,
                new_clients_col=new_clients_col,
                new_money_col=new_money_col,
                early_withdrawal_col=early_withdrawal_col,
            )

            if product_warnings:
                st.write(f"**{translate(lang, 'eligibility_warning')}:**")

                for warning in product_warnings:
                    st.write(f"- {warning}")

            if alerts_col:
                st.write(f"**{translate(lang, 'alerts')}:**")
                st.write(get_series_value(row, alerts_col, "No alerts"))

            if notes_col:
                st.write(f"**{translate(lang, 'notes_conditions')}:**")
                st.write(get_series_value(row, notes_col, "No notes available"))

            if source_col:
                source_value = get_series_value(row, source_col, "")

                if pd.notna(source_value) and str(source_value).strip():
                    st.write(f"**{translate(lang, 'official_source')}:**")
                    st.write(source_value)

    st.markdown(f"## {translate(lang, 'downloads')}")

    download_col1, download_col2 = st.columns(2)

    with download_col1:
        csv_data = ranking.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label=translate(lang, "download_csv"),
            data=csv_data,
            file_name="term_deposit_ranking.csv",
            mime="text/csv",
        )

    with download_col2:
        excel_data = to_excel_bytes(ranking)

        st.download_button(
            label=translate(lang, "download_excel"),
            data=excel_data,
            file_name="term_deposit_ranking.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.divider()

st.markdown(
    f"""
    <div class="footer-box">
        <div class="small-muted">
            {translate(lang, "footer_built")}<br>
            {translate(lang, "dataset_reference_date")}: {metadata.get("reference_date", "Not available")} |
            {translate(lang, "last_manual_validation")}: {metadata.get("last_manual_validation", "Not available")}<br><br>
            🔗 <a href="{LIVE_APP_URL}" target="_blank">{translate(lang, "live_app")}</a> |
            💻 <a href="{GITHUB_URL}" target="_blank">{translate(lang, "github_repo")}</a><br><br>
            {translate(lang, "footer_warning")}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
