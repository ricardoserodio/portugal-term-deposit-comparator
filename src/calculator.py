import pandas as pd


DATA_PATH = "data/depositos_prazo_core_portugal_corrigido.csv"


def load_data(path=DATA_PATH):
    """Load the term deposit dataset."""
    return pd.read_csv(path)


def prepare_data(df):
    """Prepare numeric and text columns."""
    df = df.copy()

    numeric_cols = [
        "TANB (%)",
        "Prazo (meses)",
        "Mínimo (€)",
        "Máximo (€)",
        "Taxa IRS",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    text_cols = [
        "Banco",
        "Produto",
        "Só novos clientes",
        "Só novos montantes",
        "Mobilização antecipada",
        "IRS aplicável",
        "Notas / condições",
        "Validação rápida",
        "Observação de validação",
        "Fonte oficial / referência",
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    return df


def generate_alerts(row):
    """Generate product condition alerts."""
    alerts = []

    if str(row["Só novos clientes"]).lower() in ["sim", "ver notas"]:
        alerts.append("Só novos clientes")

    if str(row["Só novos montantes"]).lower() == "sim":
        alerts.append("Só novos montantes")

    if str(row["Mobilização antecipada"]).lower() == "ver notas":
        alerts.append("Mobilização antecipada: ver notas")

    if pd.notna(row["Máximo (€)"]):
        alerts.append("Tem montante máximo")

    if str(row["Validação rápida"]).lower() != "validado rápido":
        alerts.append("Validação parcial")

    if not alerts:
        return "Sem alertas relevantes"

    return " | ".join(alerts)


def compare_deposits(
    df,
    capital,
    maturity_months=None,
    require_early_withdrawal=False,
    accept_new_clients_only=True,
    accept_new_money_only=True,
    top_n=10,
):
    """Compare eligible deposits and rank them by estimated net interest."""
    result = df.copy()

    result = result[
        result["Mínimo (€)"].isna() | (capital >= result["Mínimo (€)"])
    ]

    result = result[
        result["Máximo (€)"].isna() | (capital <= result["Máximo (€)"])
    ]

    if maturity_months is not None:
        result = result[result["Prazo (meses)"] == maturity_months]

    if require_early_withdrawal:
        result = result[
            result["Mobilização antecipada"]
            .str.lower()
            .isin(["sim", "ver notas"])
        ]

    if not accept_new_clients_only:
        result = result[
            ~result["Só novos clientes"]
            .str.lower()
            .isin(["sim", "ver notas"])
        ]

    if not accept_new_money_only:
        result = result[
            result["Só novos montantes"].str.lower() != "sim"
        ]

    result["Juro bruto estimado (€)"] = (
        capital
        * (result["TANB (%)"] / 100)
        * (result["Prazo (meses)"] / 12)
    )

    result["IRS estimado (€)"] = (
        result["Juro bruto estimado (€)"] * result["Taxa IRS"]
    )

    result["Juro líquido estimado (€)"] = (
        result["Juro bruto estimado (€)"] - result["IRS estimado (€)"]
    )

    result["Montante final estimado (€)"] = (
        capital + result["Juro líquido estimado (€)"]
    )

    result["Alertas"] = result.apply(generate_alerts, axis=1)

    money_cols = [
        "Juro bruto estimado (€)",
        "IRS estimado (€)",
        "Juro líquido estimado (€)",
        "Montante final estimado (€)",
    ]

    result[money_cols] = result[money_cols].round(2)

    result = result.sort_values(
        by="Juro líquido estimado (€)",
        ascending=False,
    )

    columns = [
        "Banco",
        "Produto",
        "Prazo (meses)",
        "TANB (%)",
        "Juro bruto estimado (€)",
        "IRS estimado (€)",
        "Juro líquido estimado (€)",
        "Montante final estimado (€)",
        "Alertas",
        "Notas / condições",
        "Fonte oficial / referência",
    ]

    return result[columns].head(top_n)


if __name__ == "__main__":
    df = load_data()
    df = prepare_data(df)

    ranking = compare_deposits(
        df=df,
        capital=10000,
        maturity_months=12,
        require_early_withdrawal=False,
        accept_new_clients_only=True,
        accept_new_money_only=True,
        top_n=10,
    )

    print(ranking)
