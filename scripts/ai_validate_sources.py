import os
import csv
import json
import re
from datetime import date
from io import BytesIO
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


DATASET_PATH = "data/depositos_prazo_core_portugal_corrigido.csv"
SOURCE_LINKS_PATH = "data/source_links.csv"
VALIDATION_LOG_PATH = "validation/bank_rate_validation_log.csv"

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")


def normalize_value(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def extract_url_from_text(text):
    urls = re.findall(r"https?://[^\s,;]+", str(text))
    return urls[0] if urls else None


def detect_source_type(url):
    path = urlparse(url).path.lower()
    if path.endswith(".pdf"):
        return "Official PDF"
    return "Official Page"


def fetch_source_text(url):
    print(f"\nFetching official source:\n{url}\n")

    response = requests.get(
        url,
        timeout=40,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()

    if detect_source_type(url) == "Official PDF":
        reader = PdfReader(BytesIO(response.content))
        text = []
        for page in reader.pages:
            text.append(page.extract_text() or "")
        return "\n".join(text)

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    return soup.get_text(separator="\n")


def choose_source(source_links_df, bank, product):
    search_text = f"{bank} {product}".lower()

    candidates = source_links_df[
        source_links_df.astype(str).apply(
            lambda row: str(bank).lower() in " ".join(row.values).lower(),
            axis=1
        )
    ].reset_index(drop=True)

    if candidates.empty:
        print("\nNo source found in source_links.csv.")
        return input("Paste official source URL manually: ").strip()

    print("\nPossible official sources:")
    for i, row in candidates.iterrows():
        row_text = " | ".join(str(x) for x in row.values)
        print(f"{i + 1}. {row_text[:300]}")

    choice = input("\nChoose source number, or press Enter to paste manually: ").strip()

    if not choice:
        return input("Paste official source URL manually: ").strip()

    selected = candidates.iloc[int(choice) - 1]
    selected_text = " ".join(str(x) for x in selected.values)
    url = extract_url_from_text(selected_text)

    if not url:
        return input("Could not find URL. Paste official source URL manually: ").strip()

    return url


def ai_extract_data(source_text, bank, product):
    source_text = source_text[:30000]

    schema = {
        "type": "object",
        "properties": {
            "bank": {"type": ["string", "null"]},
            "product": {"type": ["string", "null"]},
            "maturity_months": {"type": ["number", "null"]},
            "tanb_percent": {"type": ["number", "null"]},
            "min_amount_eur": {"type": ["number", "null"]},
            "max_amount_eur": {"type": ["number", "null"]},
            "new_clients_only": {"type": ["boolean", "null"]},
            "new_money_required": {"type": ["boolean", "null"]},
            "early_withdrawal_allowed": {"type": ["boolean", "null"]},
            "early_withdrawal_penalty": {"type": ["string", "null"]},
            "interest_payment": {"type": ["string", "null"]},
            "renewal": {"type": ["string", "null"]},
            "source_confidence": {
                "type": "string",
                "enum": ["low", "medium", "high"]
            },
            "evidence_summary": {"type": "string"},
            "warnings": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": [
            "bank",
            "product",
            "maturity_months",
            "tanb_percent",
            "min_amount_eur",
            "max_amount_eur",
            "new_clients_only",
            "new_money_required",
            "early_withdrawal_allowed",
            "early_withdrawal_penalty",
            "interest_payment",
            "renewal",
            "source_confidence",
            "evidence_summary",
            "warnings"
        ],
        "additionalProperties": False
    }

    prompt = f"""
You are validating a Portuguese term deposit dataset against an official bank source.

Extract only information explicitly present in the source text.
Do not guess. If a field is unclear, return null.

Target bank: {bank}
Target product: {product}

Important:
- TANB means gross annual nominal rate.
- Amounts must be returned as numbers in EUR.
- If several maturities exist, focus on the product/maturity shown in the selected dataset row if identifiable.
- Evidence summary must explain what was found and what remains uncertain.

Official source text:
\"\"\"
{source_text}
\"\"\"
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "term_deposit_validation",
                "schema": schema,
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)


def compare_numeric(dataset_value, official_value):
    if official_value is None:
        return "Unknown"

    dataset_value = normalize_value(dataset_value)

    try:
        d = float(
            str(dataset_value)
            .replace("%", "")
            .replace("€", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )
        o = float(official_value)
        return "Yes" if abs(d - o) < 0.01 else "No"
    except Exception:
        return "Unknown"


def compare_boolean(dataset_value, official_value):
    if official_value is None:
        return "Unknown"

    text = normalize_value(dataset_value).lower()

    if text in ["sim", "yes", "true", "1"]:
        dataset_bool = True
    elif text in ["não", "nao", "no", "false", "0"]:
        dataset_bool = False
    else:
        return "Unknown"

    return "Yes" if dataset_bool == official_value else "No"


def get_column(row, possible_names):
    for name in possible_names:
        if name in row.index:
            return row[name]
    return ""


def append_to_log(log_row):
    with open(VALIDATION_LOG_PATH, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(log_row)


def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not found. Create a local .env file first.")

    dataset = pd.read_csv(DATASET_PATH)
    source_links = pd.read_csv(SOURCE_LINKS_PATH)

    banks = sorted(dataset.iloc[:, 0].dropna().unique())

    print("\nAvailable banks:")
    for i, bank in enumerate(banks, start=1):
        print(f"{i}. {bank}")

    bank_choice = int(input("\nChoose bank number: ").strip())
    selected_bank = banks[bank_choice - 1]

    bank_rows = dataset[dataset.iloc[:, 0] == selected_bank].reset_index(drop=True)

    print(f"\nProducts for {selected_bank}:")
    for i, row in bank_rows.iterrows():
        preview = " | ".join(str(x) for x in row.values[:8])
        print(f"{i + 1}. {preview}")

    product_choice = int(input("\nChoose product row number: ").strip())
    selected_row = bank_rows.iloc[product_choice - 1]

    bank = selected_row.iloc[0]
    product = selected_row.iloc[1]

    print("\nSelected dataset row:")
    print(selected_row.to_string())

    source_url = choose_source(source_links, bank, product)
    source_type = detect_source_type(source_url)

    source_text = fetch_source_text(source_url)

    print("\nSending source text to AI...\n")
    extracted = ai_extract_data(source_text, bank, product)

    print("\nAI extraction:")
    print(json.dumps(extracted, indent=2, ensure_ascii=False))

    dataset_tanb = get_column(selected_row, ["tanb", "TANB", "TANB (%)", "taxa_tanb", "tanb_percent"])
    dataset_min = get_column(selected_row, ["min_amount", "Montante mínimo", "montante_minimo", "min_amount_eur"])
    dataset_max = get_column(selected_row, ["max_amount", "Montante máximo", "montante_maximo", "max_amount_eur"])
    dataset_early = get_column(selected_row, ["early_withdrawal", "Mobilização antecipada", "mobilizacao_antecipada"])

    tanb_match = compare_numeric(dataset_tanb, extracted["tanb_percent"])
    min_match = compare_numeric(dataset_min, extracted["min_amount_eur"])
    max_match = compare_numeric(dataset_max, extracted["max_amount_eur"])
    early_match = compare_boolean(dataset_early, extracted["early_withdrawal_allowed"])

    print("\nComparison:")
    print(f"TANB: dataset={dataset_tanb} | official={extracted['tanb_percent']} | match={tanb_match}")
    print(f"Min amount: dataset={dataset_min} | official={extracted['min_amount_eur']} | match={min_match}")
    print(f"Max amount: dataset={dataset_max} | official={extracted['max_amount_eur']} | match={max_match}")
    print(f"Early withdrawal: dataset={dataset_early} | official={extracted['early_withdrawal_allowed']} | match={early_match}")

    print("\nEvidence summary:")
    print(extracted["evidence_summary"])

    if extracted["warnings"]:
        print("\nWarnings:")
        for warning in extracted["warnings"]:
            print(f"- {warning}")

    approve = input("\nApprove validation and write to log? y/n: ").strip().lower()

    if approve != "y":
        print("\nNot approved. Nothing was written.")
        return

    validation_status = "Validated_FIN" if source_type == "Official PDF" and extracted["source_confidence"] == "high" else "Partially_Validated"

    log_row = [
        date.today().isoformat(),
        bank,
        product,
        extracted["maturity_months"],
        dataset_tanb,
        extracted["tanb_percent"],
        tanb_match,
        dataset_min,
        extracted["min_amount_eur"],
        min_match,
        dataset_max,
        extracted["max_amount_eur"],
        max_match,
        dataset_early,
        extracted["early_withdrawal_allowed"],
        early_match,
        source_type,
        source_url,
        validation_status,
        extracted["evidence_summary"]
    ]

    append_to_log(log_row)

    print(f"\nValidation written to {VALIDATION_LOG_PATH}")


if __name__ == "__main__":
    main()
