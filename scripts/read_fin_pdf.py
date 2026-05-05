import re
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parents[1]

INCOMING_FIN_DIR = BASE_DIR / "incoming_fin"
VALIDATION_DIR = BASE_DIR / "validation"
OUTPUT_PATH = VALIDATION_DIR / "fin_pdf_review.md"


# ------------------------------------------------------------
# Text cleaning
# ------------------------------------------------------------

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_for_detection(text: str) -> str:
    """
    Creates a detection-friendly version of the PDF text.
    Useful for PDFs where fields are extracted in uppercase or with broken spacing.
    """
    text = clean_text(text)
    text = text.replace("º", "o")
    text = text.replace("ª", "a")
    return text


def read_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))

    pages_text = []

    for page in reader.pages:
        extracted = page.extract_text() or ""
        pages_text.append(extracted)

    return clean_text("\n".join(pages_text))


def find_first_match(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)

        if match:
            if match.groups():
                return clean_text(match.group(1))
            return clean_text(match.group(0))

    return "Not detected"


# ------------------------------------------------------------
# Generic detectors
# ------------------------------------------------------------

def detect_bank(text: str) -> str:
    upper = text.upper()

    if "BANCO DE INVESTIMENTO GLOBAL" in upper or "WWW.BIG.PT" in upper:
        return "Banco de Investimento Global"

    if "BANCO BAI EUROPA" in upper or "BAI EUROPA" in upper:
        return "Banco BAI Europa"

    return find_first_match(
        text,
        [
            r"(Banco\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ\s]+)",
            r"(Caixa\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ\s]+)",
        ],
    )


def detect_product_generic(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Designação\s+(.+?)\s+Condições de acesso",
            r"Designação\s+(.+?)\s+Modalidade",
            r"(Depósito a Prazo [A-Za-zÀ-ÿ0-9\s\-\+]+)",
            r"(Super Depósito [A-Za-zÀ-ÿ0-9\s\-\+]+)",
            r"(Invest Choice [A-Za-zÀ-ÿ0-9\s\-\+]+)",
        ],
    )


def detect_maturity_generic(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Prazo\s+(.+?)\s+Na constituição",
            r"Prazo\s+(.+?)\s+Mobilização antecipada",
            r"Prazo\s+(.+?)\s+Renovação",
            r"(\d+\s*meses(?:\s*\(\d+\s*dias\))?(?:\s*ou\s*\d+\s*meses(?:\s*\(\d+\s*dias\))?)?)",
            r"(\d+\s*meses)",
        ],
    )


def detect_minimum_amount_generic(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Montante mínimo de constituição:\s*(EUR\s*[\d\.\,]+)",
            r"Montante mínimo[^:]*:\s*(EUR\s*[\d\.\,]+)",
            r"Mínimo[^:]*:\s*(EUR\s*[\d\.\,]+)",
            r"Montante mínimo[^0-9]*(\d[\d\.\,]+\s*EUR)",
            r"Mínimo[^0-9]*(\d[\d\.\,]+\s*EUR)",
        ],
    )


def detect_maximum_amount_generic(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Montante máximo de constituição:\s*(EUR\s*[\d\.\,]+)",
            r"Montante máximo[^:]*:\s*(EUR\s*[\d\.\,]+)",
            r"Máximo[^:]*:\s*(EUR\s*[\d\.\,]+)",
            r"Montante máximo[^0-9]*(\d[\d\.\,]+\s*EUR)",
            r"Máximo[^0-9]*(\d[\d\.\,]+\s*EUR)",
        ],
    )


def detect_early_withdrawal_generic(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Mobilização antecipada\s+(.+?)\s+Renovação",
            r"Mobilização antecipada\s+(.+?)\s+Moeda",
            r"Mobilização antecipada\s+(.+?)\s+Montante",
            r"Mobilizações\s+(.+?)\s+Renovações",
            r"Mobilização\s+(.+?)\s+Renovação",
        ],
    )


def detect_renewal_generic(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Renovação\s+(.+?)\s+Moeda",
            r"Renovação\s+(.+?)\s+Montante",
            r"Renovações\s+(.+?)\s+Mobilizações",
            r"Não renovável",
            r"Não permite renovação",
        ],
    )


def detect_tax_regime_generic(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Regime fiscal\s+(.+?)\s+Instituição depositária",
            r"Regime fiscal\s+(.+?)\s+Garantia de capital",
            r"Residentes:\s+(.+?)\s+Não Residentes",
        ],
    )


def detect_tanb_generic(text: str) -> str:
    """
    Generic TANB detector.
    Conservative because PDFs often include fiscal percentages that are not TANB.
    """
    upper = text.upper()

    if "TANB" not in upper and "TAXA ANUAL NOMINAL BRUTA" not in upper:
        return "Requires visual confirmation"

    # Try to capture percentages near TANB references.
    tanb_contexts = re.findall(
        r"(?:TANB|TAXA ANUAL NOMINAL BRUTA).{0,250}",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    percentages = []

    for context in tanb_contexts:
        found = re.findall(r"\d+[,\.]\d+\s*%", context)
        percentages.extend(found)

    unique = []
    for value in percentages:
        clean = value.replace(" ", "")
        if clean not in unique:
            unique.append(clean)

    if unique:
        return "; ".join(unique[:10])

    return "Requires visual confirmation"


def detect_document_version(text: str) -> str:
    return find_first_match(
        text,
        [
            r"(FINDP\.v\d+\.\d+)",
            r"(FIN[A-Z]*\.v\d+\.\d+)",
            r"(v\d+\.\d+)",
        ],
    )


# ------------------------------------------------------------
# Banco BiG specific detector
# ------------------------------------------------------------

def is_big_pdf(text: str) -> bool:
    upper = text.upper()
    return (
        "BANCO DE INVESTIMENTO GLOBAL" in upper
        or "WWW.BIG.PT" in upper
        or "APOIO@BIG.PT" in upper
        or "BIG.PT" in upper
    )


def detect_big_product(text: str, file_name: str) -> str:
    upper = text.upper()
    file_upper = file_name.upper()

    if "SUPER DEPÓSITO 3 MESES" in upper or "SUPER DEPOSITO 3 MESES" in upper:
        return "Super Depósito 3 Meses"

    if "SUPER DEPÓSITO" in upper or "SUPER DEPOSITO" in upper:
        return "Super Depósito"

    if "PTDP2025074" in upper or "PTDP2025074" in file_upper:
        return "Super Depósito 3 Meses"

    return detect_product_generic(text)


def detect_big_maturity(text: str, file_name: str) -> str:
    upper = text.upper()
    file_upper = file_name.upper()

    if "3 MESES" in upper or "3_MESES" in file_upper:
        return "3 meses"

    result = find_first_match(
        text,
        [
            r"PRAZO\s+(.+?)\s+TANB",
            r"PRAZO\s+(.+?)\s+TAXA",
            r"(\d+\s*MESES)",
            r"(\d+\s*meses)",
        ],
    )

    return result


def detect_big_tanb(text: str) -> str:
    """
    BiG PDFs often extract text in a difficult order.
    This detector searches for percentages near TANB / taxa de remuneração.
    It avoids fiscal rates if possible.
    """
    upper = text.upper()

    contexts = []

    for keyword in ["TANB", "TAXA ANUAL NOMINAL BRUTA", "TAXA DE REMUNERAÇÃO", "TAXA DE REMUNERACAO"]:
        for match in re.finditer(keyword, upper):
            start = max(match.start() - 150, 0)
            end = min(match.end() + 350, len(text))
            contexts.append(text[start:end])

    percentages = []

    for context in contexts:
        found = re.findall(r"\d+[,\.]\d+\s*%", context)
        percentages.extend(found)

    # Remove obvious fiscal rates often found in Portuguese FINs.
    fiscal_rates = {"28%", "25%", "35%", "19,6%", "17,5%", "19.6%", "17.5%"}

    unique = []
    for value in percentages:
        clean = value.replace(" ", "")
        if clean not in fiscal_rates and clean not in unique:
            unique.append(clean)

    if unique:
        return "; ".join(unique[:10])

    return "Requires visual confirmation"


def detect_big_minimum_amount(text: str) -> str:
    result = find_first_match(
        text,
        [
            r"MONTANTE\s+MÍNIMO\s+(.+?)\s+MONTANTE",
            r"MONTANTE\s+MINIMO\s+(.+?)\s+MONTANTE",
            r"MONTANTE\s+MÍNIMO[^0-9]*(\d[\d\.\,]+\s*EUR)",
            r"MONTANTE\s+MINIMO[^0-9]*(\d[\d\.\,]+\s*EUR)",
            r"MÍNIMO[^0-9]*(\d[\d\.\,]+\s*EUR)",
            r"MINIMO[^0-9]*(\d[\d\.\,]+\s*EUR)",
        ],
    )

    return result


def detect_big_maximum_amount(text: str) -> str:
    result = find_first_match(
        text,
        [
            r"MONTANTE\s+MÁXIMO\s+(.+?)\s+MOBILIZA",
            r"MONTANTE\s+MAXIMO\s+(.+?)\s+MOBILIZA",
            r"MONTANTE\s+MÁXIMO[^0-9]*(\d[\d\.\,]+\s*EUR)",
            r"MONTANTE\s+MAXIMO[^0-9]*(\d[\d\.\,]+\s*EUR)",
            r"MÁXIMO[^0-9]*(\d[\d\.\,]+\s*EUR)",
            r"MAXIMO[^0-9]*(\d[\d\.\,]+\s*EUR)",
        ],
    )

    return result


def detect_big_early_withdrawal(text: str) -> str:
    upper = text.upper()

    if "NÃO MOBILIZÁVEL" in upper or "NAO MOBILIZAVEL" in upper:
        return "Não permite mobilização antecipada"

    if "MOBILIZAÇÃO ANTECIPADA" in upper or "MOBILIZACAO ANTECIPADA" in upper:
        return find_first_match(
            text,
            [
                r"MOBILIZAÇÃO ANTECIPADA\s+(.+?)\s+RENOVA",
                r"MOBILIZACAO ANTECIPADA\s+(.+?)\s+RENOVA",
                r"MOBILIZAÇÃO ANTECIPADA\s+(.+?)\s+REGIME",
                r"MOBILIZACAO ANTECIPADA\s+(.+?)\s+REGIME",
            ],
        )

    return "Requires manual confirmation"


def detect_big_renewal(text: str) -> str:
    upper = text.upper()

    if "NÃO RENOVÁVEL" in upper or "NAO RENOVAVEL" in upper:
        return "Não renovável"

    if "RENOVÁVEL" in upper or "RENOVAVEL" in upper:
        return "Renovável"

    return find_first_match(
        text,
        [
            r"RENOVAÇÃO\s+(.+?)\s+CAPITALIZAÇÃO",
            r"RENOVACAO\s+(.+?)\s+CAPITALIZACAO",
            r"RENOVAÇÃO\s+(.+?)\s+TAXA",
            r"RENOVACAO\s+(.+?)\s+TAXA",
        ],
    )


# ------------------------------------------------------------
# Summary logic
# ------------------------------------------------------------

def build_confidence(summary: dict) -> str:
    detected_count = 0
    total = 7

    fields = [
        "bank",
        "product",
        "maturity",
        "tanb",
        "minimum_amount",
        "maximum_amount",
        "early_withdrawal",
        "renewal",
    ]

    for field in fields:
        value = summary.get(field, "")
        if value and value not in ["Not detected", "Requires visual confirmation", "Requires manual confirmation"]:
            detected_count += 1

    if detected_count >= 6:
        return "High"

    if detected_count >= 4:
        return "Medium"

    return "Low"


def summarize_pdf(pdf_path: Path) -> dict:
    text = read_pdf_text(pdf_path)
    normalized_text = normalize_for_detection(text)

    if is_big_pdf(normalized_text):
        summary = {
            "file_name": pdf_path.name,
            "bank": "Banco de Investimento Global",
            "product": detect_big_product(normalized_text, pdf_path.name),
            "maturity": detect_big_maturity(normalized_text, pdf_path.name),
            "tanb": detect_big_tanb(normalized_text),
            "minimum_amount": detect_big_minimum_amount(normalized_text),
            "maximum_amount": detect_big_maximum_amount(normalized_text),
            "early_withdrawal": detect_big_early_withdrawal(normalized_text),
            "renewal": detect_big_renewal(normalized_text),
            "tax_regime": detect_tax_regime_generic(normalized_text),
            "document_version": detect_document_version(normalized_text),
            "parser_used": "Banco BiG specific parser",
            "text_preview": normalized_text[:3000],
        }
    else:
        summary = {
            "file_name": pdf_path.name,
            "bank": detect_bank(normalized_text),
            "product": detect_product_generic(normalized_text),
            "maturity": detect_maturity_generic(normalized_text),
            "tanb": detect_tanb_generic(normalized_text),
            "minimum_amount": detect_minimum_amount_generic(normalized_text),
            "maximum_amount": detect_maximum_amount_generic(normalized_text),
            "early_withdrawal": detect_early_withdrawal_generic(normalized_text),
            "renewal": detect_renewal_generic(normalized_text),
            "tax_regime": detect_tax_regime_generic(normalized_text),
            "document_version": detect_document_version(normalized_text),
            "parser_used": "Generic parser",
            "text_preview": normalized_text[:3000],
        }

    summary["extraction_confidence"] = build_confidence(summary)

    if summary["tanb"] in ["Requires visual confirmation", "Not detected"]:
        summary["manual_review_required"] = "Yes - TANB requires visual confirmation"
    elif summary["extraction_confidence"] in ["Low", "Medium"]:
        summary["manual_review_required"] = "Yes - review extracted fields before validation"
    else:
        summary["manual_review_required"] = "Review recommended before dataset update"

    return summary


def write_review(summaries: list[dict]) -> None:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        file.write("# FIN/PDF Validation Review\n\n")
        file.write(f"Generated at: {now}\n\n")
        file.write(
            "This document summarizes the fields extracted from official FIN/PDF documents. "
            "The extraction is semi-automatic and should be reviewed before updating the dataset.\n\n"
        )
        file.write("---\n\n")

        for index, item in enumerate(summaries, start=1):
            file.write(f"## {index}. {item['bank']} — {item['product']}\n\n")

            file.write(f"**Source file:** `incoming_fin/{item['file_name']}`\n\n")
            file.write(f"**Parser used:** {item['parser_used']}\n\n")
            file.write(f"**Document version:** {item['document_version']}\n\n")
            file.write(f"**Extraction confidence:** {item['extraction_confidence']}\n\n")
            file.write(f"**Manual review required:** {item['manual_review_required']}\n\n")

            file.write("### Extracted Fields\n\n")
            file.write(f"- **Bank:** {item['bank']}\n")
            file.write(f"- **Product:** {item['product']}\n")
            file.write(f"- **Maturity / Prazo:** {item['maturity']}\n")
            file.write(f"- **TANB:** {item['tanb']}\n")
            file.write(f"- **Minimum Amount / Montante mínimo:** {item['minimum_amount']}\n")
            file.write(f"- **Maximum Amount / Montante máximo:** {item['maximum_amount']}\n")
            file.write(f"- **Early Withdrawal / Mobilização antecipada:** {item['early_withdrawal']}\n")
            file.write(f"- **Renewal / Renovação:** {item['renewal']}\n")
            file.write(f"- **Tax Regime / Regime fiscal:** {item['tax_regime']}\n\n")

            file.write("### Human Validation\n\n")
            file.write("**Human Decision:** \n\n")
            file.write("Use one of: `Validated`, `Update dataset`, `Keep under review`, `Source unavailable`\n\n")

            file.write("**Validator Notes:** \n\n")
            file.write("Example:\n\n")
            file.write(
                "> FIN oficial consultada. Produto, prazo, TANB, montante mínimo/máximo, "
                "mobilização antecipada e renovação confirmados. Valores coincidem com o dataset.\n\n"
            )

            file.write("### Extracted Text Preview\n\n")
            file.write("```text\n")
            file.write(item["text_preview"])
            file.write("\n```\n\n")

            file.write("---\n\n")


def main():
    INCOMING_FIN_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(INCOMING_FIN_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in incoming_fin/")
        print("Add one or more FIN/PDF files and run again.")
        return

    summaries = []

    for pdf_path in pdf_files:
        print(f"Reading: {pdf_path}")
        summaries.append(summarize_pdf(pdf_path))

    write_review(summaries)

    print("\nFIN/PDF validation review created successfully:")
    print(OUTPUT_PATH)
    print("\nOpen it with:")
    print("code validation/fin_pdf_review.md")


if __name__ == "__main__":
    main()
