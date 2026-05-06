import re
import pandas as pd


DATASET_PATH = "data/depositos_prazo_core_portugal_corrigido.csv"
SOURCE_LINKS_PATH = "data/source_links.csv"

COVERAGE_REPORT_PATH = "validation/source_coverage_report.csv"
MISSING_TEMPLATE_PATH = "validation/source_links_missing_template.csv"


def read_csv_flexible(path):
    # source_links uses |, dataset usually uses comma
    for sep in ["|", ";", ","]:
        try:
            df = pd.read_csv(path, sep=sep, encoding="utf-8-sig", dtype=str)
            if len(df.columns) > 1:
                return df, sep
        except Exception:
            pass

    raise ValueError(f"Could not read CSV properly: {path}")


def normalize(value):
    if pd.isna(value):
        return ""

    text = str(value).strip().lower()

    replacements = {
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ç": "c",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text


def product_tokens(product):
    generic = {
        "deposito",
        "depositos",
        "prazo",
        "prazos",
        "mes",
        "meses",
        "cliente",
        "clientes",
        "novo",
        "novos",
        "nova",
        "novas",
        "montante",
        "montantes",
        "particular",
        "particulares",
        "taxa",
        "tanb",
        "fin",
        "pdf",
    }

    text = normalize(product)

    tokens = [
        token
        for token in re.findall(r"[a-z0-9]+", text)
        if token not in generic and len(token) > 1
    ]

    return set(tokens)


def get_first_col(df, possible_names, fallback_index=None):
    for name in possible_names:
        if name in df.columns:
            return name

    if fallback_index is not None and fallback_index < len(df.columns):
        return df.columns[fallback_index]

    return None


def source_match_level(dataset_bank, dataset_product, sources):
    bank_norm = normalize(dataset_bank)
    product_norm = normalize(dataset_product)
    tokens = product_tokens(dataset_product)

    exact_matches = []
    product_token_matches = []
    bank_only_matches = []

    for _, source in sources.iterrows():
        source_text = " ".join(str(x) for x in source.values)
        source_norm = normalize(source_text)

        if bank_norm not in source_norm:
            continue

        bank_only_matches.append(source)

        source_product = normalize(source.get("Produto", ""))

        if product_norm == source_product:
            exact_matches.append(source)
            continue

        if tokens and any(token in re.findall(r"[a-z0-9]+", source_norm) for token in tokens):
            product_token_matches.append(source)

    if exact_matches:
        return "Exact_Product_Source", exact_matches[0]

    if product_token_matches:
        return "Product_Token_Source", product_token_matches[0]

    if bank_only_matches:
        return "Bank_Only_Source", bank_only_matches[0]

    return "Missing_Source", None


def main():
    dataset, dataset_sep = read_csv_flexible(DATASET_PATH)
    sources, sources_sep = read_csv_flexible(SOURCE_LINKS_PATH)

    bank_col = get_first_col(dataset, ["Banco", "bank"], fallback_index=0)
    product_col = get_first_col(dataset, ["Produto", "product"], fallback_index=1)
    maturity_col = get_first_col(dataset, ["Prazo (meses)", "maturity_months", "prazo_meses"])
    tanb_col = get_first_col(dataset, ["TANB (%)", "tanb", "TANB", "tanb_percent"])
    min_col = get_first_col(dataset, ["Mínimo (€)", "min_amount", "min_amount_eur"])
    max_col = get_first_col(dataset, ["Máximo (€)", "max_amount", "max_amount_eur"])

    required_source_cols = [
        "Banco",
        "Produto",
        "Tipo Fonte",
        "URL",
        "Campo a validar",
        "Estado auditoria",
        "Ativo",
        "Notas auditoria",
    ]

    for col in required_source_cols:
        if col not in sources.columns:
            raise ValueError(f"Missing column in source_links.csv: {col}")

    report_rows = []
    missing_rows = []

    for _, row in dataset.iterrows():
        bank = row.get(bank_col, "")
        product = row.get(product_col, "")

        level, matched_source = source_match_level(bank, product, sources)

        matched_url = ""
        matched_product = ""
        matched_type = ""

        if matched_source is not None:
            matched_url = matched_source.get("URL", "")
            matched_product = matched_source.get("Produto", "")
            matched_type = matched_source.get("Tipo Fonte", "")

        report_rows.append({
            "bank": bank,
            "product": product,
            "maturity_months": row.get(maturity_col, "") if maturity_col else "",
            "tanb": row.get(tanb_col, "") if tanb_col else "",
            "min_amount": row.get(min_col, "") if min_col else "",
            "max_amount": row.get(max_col, "") if max_col else "",
            "coverage_status": level,
            "matched_source_product": matched_product,
            "matched_source_type": matched_type,
            "matched_source_url": matched_url,
        })

        if level == "Missing_Source":
            missing_rows.append({
                "Banco": bank,
                "Produto": product,
                "Tipo Fonte": "TODO",
                "URL": "TODO_OFFICIAL_URL",
                "Campo a validar": "TANB;Prazo;Mínimo;Máximo;Mobilização",
                "Estado auditoria": "Por auditar",
                "Ativo": "Sim",
                "Notas auditoria": "Adicionar fonte oficial específica para este produto.",
            })

    report = pd.DataFrame(report_rows)
    missing = pd.DataFrame(missing_rows)

    report.to_csv(COVERAGE_REPORT_PATH, index=False, encoding="utf-8-sig")
    missing.to_csv(MISSING_TEMPLATE_PATH, index=False, sep="|", encoding="utf-8-sig")

    print("Source coverage audit completed.")
    print(f"Dataset rows: {len(dataset)}")
    print(f"Source links rows: {len(sources)}")
    print()
    print(report["coverage_status"].value_counts(dropna=False).to_string())
    print()
    print(f"Coverage report written to: {COVERAGE_REPORT_PATH}")
    print(f"Missing source template written to: {MISSING_TEMPLATE_PATH}")

    if len(missing) > 0:
        print()
        print("Missing products:")
        print(missing[["Banco", "Produto", "URL"]].to_string(index=False))
    else:
        print()
        print("No missing source rows found.")


if __name__ == "__main__":
    main()