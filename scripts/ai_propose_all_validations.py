import argparse
import csv
import time
from datetime import date

import pandas as pd

from ai_validate_sources import (
    DATASET_PATH,
    SOURCE_LINKS_PATH,
    fetch_source_text,
    ai_extract_data,
    compare_numeric,
    compare_boolean,
    get_column,
    extract_url_from_text,
    detect_source_type,
)


OUTPUT_PATH = "validation/proposed_validations_ai.csv"


def row_text(row):
    return " ".join(str(x) for x in row.values)


def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def product_score(source_row_text, bank, product):
    """
    Safe source matching.

    Rules:
    - Bank name must match.
    - At least one non-generic product word must match.
    - Generic words like deposito/prazo/clientes do not count as product match.
    """

    text = normalize_text(source_row_text)
    bank_text = normalize_text(bank)
    product_text = normalize_text(product)

    if bank_text not in text:
        return 0

    generic_words = {
        "deposito",
        "depósito",
        "prazo",
        "meses",
        "clientes",
        "cliente",
        "novos",
        "novo",
        "montantes",
        "montante",
        "particulares",
        "superior",
        "inferior",
        "taxa",
        "tanb",
    }

    product_words = [
        word.lower()
        for word in product_text.replace("-", " ").replace("/", " ").split()
        if len(word) > 1 and word.lower() not in generic_words
    ]

    matched_words = 0

    for word in product_words:
        if word in text:
            matched_words += 1

    # If the product has specific words, at least one must match.
    # Example: "Depósito ON" requires "on" to appear.
    # Example: "Super Depósito" requires "super" to appear.
    if product_words and matched_words == 0:
        return 0

    score = 50
    score += matched_words * 15

    if "details" in text or "página oficial" in text or "pagina oficial" in text:
        score += 15

    if "fin" in text:
        score += 8

    if "pdf" in text:
        score += 5

    if "oficial" in text or "official" in text:
        score += 5

    if "validado" in text or "validated" in text:
        score += 3

    if product_text in text:
        score += 20

    return score
    """
    Safe source matching.

    Rules:
    - Bank name must match.
    - At least one meaningful product word must match.
    - Prefer direct product pages/details over generic FIN when they are more readable.
    """

    text = normalize_text(source_row_text)
    bank_text = normalize_text(bank)
    product_text = normalize_text(product)

    # Bank must match. No bank match = no source.
    if bank_text not in text:
        return 0

    product_words = [
        word.lower()
        for word in product_text.replace("-", " ").replace("/", " ").split()
        if len(word) > 3
    ]

    matched_words = 0

    for word in product_words:
        if word in text:
            matched_words += 1

    # Product must match at least partially.
    # This prevents "Depósito ON" from using "Super Depósito" source.
    if product_words and matched_words == 0:
        return 0

    score = 50

    # Product match strength
    score += matched_words * 10

    # Prefer direct product pages/details because they are often easier for AI to parse
    if "details" in text or "página oficial" in text or "pagina oficial" in text:
        score += 15

    # FIN/PDF is valuable, but not always AI-readable
    if "fin" in text:
        score += 8

    if "pdf" in text:
        score += 5

    if "oficial" in text or "official" in text:
        score += 5

    if "validado" in text or "validated" in text:
        score += 3

    # Specific product name bonus
    if product_text in text:
        score += 20

    return score


def find_best_source(source_links_df, bank, product):
    """
    Finds the safest official source.

    If no source row contains both the bank and a meaningful product match,
    returns None instead of using a wrong source.
    """

    scored = []

    for _, source_row in source_links_df.iterrows():
        text = row_text(source_row)
        url = extract_url_from_text(text)

        if not url:
            continue

        score = product_score(text, bank, product)

        if score > 0:
            scored.append((score, url, text))

    if not scored:
        return None, None

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_url, best_text = scored[0]

    if best_score < 50:
        return None, None

    return best_url, best_text
    """
    Safer source matching.

    Main rule:
    - Never use a source if the bank name is not present in the source row text.
    - This avoids comparing CGD/BPG/Haitong products against Banco BAI Europa PDFs.
    """

    text = normalize_text(source_row_text)
    bank_text = normalize_text(bank)
    product_text = normalize_text(product)

    # Safety rule: bank must be present in the source row.
    if bank_text not in text:
        return 0

    score = 50

    product_words = [
        word.lower()
        for word in product_text.replace("-", " ").replace("/", " ").split()
        if len(word) > 3
    ]

    matched_words = 0

    for word in product_words:
        if word in text:
            score += 5
            matched_words += 1

    if "fin" in text:
        score += 10

    if "pdf" in text:
        score += 5

    if "oficial" in text or "official" in text:
        score += 5

    if "validado" in text or "validated" in text:
        score += 2

    # If product has meaningful words but none match, reduce confidence.
    if product_words and matched_words == 0:
        score -= 25

    return score


def find_best_source(source_links_df, bank, product):
    """
    Finds the safest official source.

    If no source row contains the same bank name, returns None.
    This is intentional: no source is better than a wrong source.
    """

    scored = []

    for _, source_row in source_links_df.iterrows():
        text = row_text(source_row)
        url = extract_url_from_text(text)

        if not url:
            continue

        score = product_score(text, bank, product)

        if score > 0:
            scored.append((score, url, text))

    if not scored:
        return None, None

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_url, best_text = scored[0]

    # Safety threshold.
    # If the score is too low, do not trust the source.
    if best_score < 40:
        return None, None

    return best_url, best_text


def build_proposal_row(
    selected_row,
    source_url,
    source_type,
    extracted,
    dataset_maturity,
    dataset_tanb,
    dataset_min,
    dataset_max,
    dataset_early,
    maturity_match,
    tanb_match,
    min_match,
    max_match,
    early_match,
    suggested_status,
    error_message="",
):
    bank = selected_row.iloc[0]
    product = selected_row.iloc[1]

    return {
        "proposal_date": date.today().isoformat(),
        "bank": bank,
        "product": product,
        "dataset_maturity_months": dataset_maturity,
        "official_maturity_months": extracted.get("maturity_months") if extracted else "",
        "maturity_match": maturity_match,
        "dataset_tanb": dataset_tanb,
        "official_tanb": extracted.get("tanb_percent") if extracted else "",
        "tanb_match": tanb_match,
        "dataset_min_amount": dataset_min,
        "official_min_amount": extracted.get("min_amount_eur") if extracted else "",
        "min_amount_match": min_match,
        "dataset_max_amount": dataset_max,
        "official_max_amount": extracted.get("max_amount_eur") if extracted else "",
        "max_amount_match": max_match,
        "dataset_early_withdrawal": dataset_early,
        "official_early_withdrawal": extracted.get("early_withdrawal_allowed") if extracted else "",
        "early_withdrawal_match": early_match,
        "source_confidence": extracted.get("source_confidence") if extracted else "",
        "source_type": source_type,
        "source_url": source_url,
        "suggested_status": suggested_status,
        "approve": "",
        "evidence_summary": extracted.get("evidence_summary") if extracted else "",
        "warnings": " | ".join(extracted.get("warnings", [])) if extracted else "",
        "error_message": error_message,
    }


def suggest_status(
    source_type,
    extracted,
    maturity_match,
    tanb_match,
    min_match,
    max_match,
    early_match,
):
    if extracted is None:
        return "Needs_Manual_Review"

    all_core_match = all(
        match == "Yes"
        for match in [
            maturity_match,
            tanb_match,
            min_match,
            max_match,
            early_match,
        ]
    )

    if (
        source_type == "Official PDF"
        and extracted.get("source_confidence") == "high"
        and all_core_match
    ):
        return "Ready_for_Approval"

    if tanb_match == "Yes" and extracted.get("source_confidence") in ["medium", "high"]:
        return "Partially_Validated"

    return "Needs_Manual_Review"


def process_row(selected_row, source_links_df):
    bank = selected_row.iloc[0]
    product = selected_row.iloc[1]

    dataset_maturity = get_column(
        selected_row,
        ["Prazo (meses)", "maturity_months", "prazo_meses"]
    )

    dataset_tanb = get_column(
        selected_row,
        ["TANB (%)", "tanb", "TANB", "taxa_tanb", "tanb_percent"]
    )

    dataset_min = get_column(
        selected_row,
        ["Mínimo (€)", "min_amount", "Montante mínimo", "montante_minimo", "min_amount_eur"]
    )

    dataset_max = get_column(
        selected_row,
        ["Máximo (€)", "max_amount", "Montante máximo", "montante_maximo", "max_amount_eur"]
    )

    dataset_early = get_column(
        selected_row,
        ["Mobilização antecipada", "early_withdrawal", "mobilizacao_antecipada"]
    )

    source_url, source_text_row = find_best_source(source_links_df, bank, product)

    if not source_url:
        return build_proposal_row(
            selected_row=selected_row,
            source_url="",
            source_type="",
            extracted=None,
            dataset_maturity=dataset_maturity,
            dataset_tanb=dataset_tanb,
            dataset_min=dataset_min,
            dataset_max=dataset_max,
            dataset_early=dataset_early,
            maturity_match="Unknown",
            tanb_match="Unknown",
            min_match="Unknown",
            max_match="Unknown",
            early_match="Unknown",
            suggested_status="No_Source_Found",
            error_message="No safe official source found in source_links.csv. Bank name did not match any source row.",
        )

    source_type = detect_source_type(source_url)

    try:
        source_text = fetch_source_text(source_url)

        extracted = ai_extract_data(
            source_text=source_text,
            bank=bank,
            product=product,
            selected_maturity_months=dataset_maturity,
        )

        maturity_match = compare_numeric(dataset_maturity, extracted["maturity_months"])
        tanb_match = compare_numeric(dataset_tanb, extracted["tanb_percent"])
        min_match = compare_numeric(dataset_min, extracted["min_amount_eur"])
        max_match = compare_numeric(dataset_max, extracted["max_amount_eur"])
        early_match = compare_boolean(dataset_early, extracted["early_withdrawal_allowed"])

        suggested_status = suggest_status(
            source_type=source_type,
            extracted=extracted,
            maturity_match=maturity_match,
            tanb_match=tanb_match,
            min_match=min_match,
            max_match=max_match,
            early_match=early_match,
        )

        return build_proposal_row(
            selected_row=selected_row,
            source_url=source_url,
            source_type=source_type,
            extracted=extracted,
            dataset_maturity=dataset_maturity,
            dataset_tanb=dataset_tanb,
            dataset_min=dataset_min,
            dataset_max=dataset_max,
            dataset_early=dataset_early,
            maturity_match=maturity_match,
            tanb_match=tanb_match,
            min_match=min_match,
            max_match=max_match,
            early_match=early_match,
            suggested_status=suggested_status,
        )

    except Exception as error:
        return build_proposal_row(
            selected_row=selected_row,
            source_url=source_url,
            source_type=source_type,
            extracted=None,
            dataset_maturity=dataset_maturity,
            dataset_tanb=dataset_tanb,
            dataset_min=dataset_min,
            dataset_max=dataset_max,
            dataset_early=dataset_early,
            maturity_match="Unknown",
            tanb_match="Unknown",
            min_match="Unknown",
            max_match="Unknown",
            early_match="Unknown",
            suggested_status="AI_Error",
            error_message=str(error),
        )


def write_proposals(proposals):
    if not proposals:
        print("No proposals to write.")
        return

    fieldnames = list(proposals[0].keys())

    # Excel-friendly for Portuguese Windows/Excel.
    # utf-8-sig fixes accents; semicolon opens better in PT Excel.
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(proposals)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of dataset rows to process."
    )
    parser.add_argument(
        "--bank",
        type=str,
        default=None,
        help="Optional bank name filter."
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.5,
        help="Seconds to wait between AI calls."
    )

    args = parser.parse_args()

    dataset = pd.read_csv(DATASET_PATH)
    source_links = pd.read_csv(SOURCE_LINKS_PATH)

    if args.bank:
        dataset = dataset[
            dataset.iloc[:, 0].astype(str).str.contains(args.bank, case=False, na=False)
        ]

    if args.limit:
        dataset = dataset.head(args.limit)

    print(f"\nRows to process: {len(dataset)}")
    print(f"Output file: {OUTPUT_PATH}")

    if len(dataset) == 0:
        print("No dataset rows found for this filter.")
        return

    confirm = input("\nThis will call the OpenAI API for each row. Type YES to continue: ").strip()

    if confirm != "YES":
        print("Cancelled.")
        return

    proposals = []

    for index, selected_row in dataset.iterrows():
        bank = selected_row.iloc[0]
        product = selected_row.iloc[1]

        print("\n" + "=" * 80)
        print(f"Processing row {index + 1}: {bank} | {product}")

        proposal = process_row(selected_row, source_links)
        proposals.append(proposal)

        print(f"Suggested status: {proposal['suggested_status']}")
        print(f"TANB match: {proposal['tanb_match']}")
        print(f"Maturity match: {proposal['maturity_match']}")
        print(f"Min match: {proposal['min_amount_match']}")
        print(f"Max match: {proposal['max_amount_match']}")
        print(f"Early withdrawal match: {proposal['early_withdrawal_match']}")

        if proposal["source_url"]:
            print(f"Source used: {proposal['source_url']}")
        else:
            print("Source used: none")

        if proposal["error_message"]:
            print(f"Error/message: {proposal['error_message']}")

        # Write progressively, so progress is not lost if something fails.
        write_proposals(proposals)

        time.sleep(args.sleep)

    print("\nFinished.")
    print(f"Proposals written to: {OUTPUT_PATH}")
    print("\nNext step:")
    print("1. Review proposed_validations_ai.csv")
    print("2. Approve rows manually or run mark_ready_proposals_as_approved.py")
    print("3. Run apply_approved_validations.py")


if __name__ == "__main__":
    main()