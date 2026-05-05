import re
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


BASE_DIR = Path(__file__).resolve().parents[1]

INCOMING_FIN_DIR = BASE_DIR / "incoming_fin"
VALIDATION_DIR = BASE_DIR / "validation"
OUTPUT_PATH = VALIDATION_DIR / "fin_pdf_review.md"


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def read_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))

    pages_text = []

    for page in reader.pages:
        extracted = page.extract_text() or ""
        pages_text.append(extracted)

    return clean_text("\n".join(pages_text))


def find_first_match(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            if match.groups():
                return clean_text(match.group(1))
            return clean_text(match.group(0))

    return "Not detected"


def detect_bank(text: str) -> str:
    return find_first_match(
        text,
        [
            r"(Banco\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]+Europa)",
            r"(Banco\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]+)",
            r"(Caixa\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]+)",
        ],
    )


def detect_product(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Designação\s+(.+?)\s+Condições de acesso",
            r"(Depósito a Prazo [A-Za-zÀ-ÿ0-9\s\-]+)",
            r"(Super Depósito [A-Za-zÀ-ÿ0-9\s\-]+)",
            r"(Invest Choice [A-Za-zÀ-ÿ0-9\s\-]+)",
        ],
    )


def detect_maturity(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Prazo\s+(.+?)\s+Na constituição",
            r"Prazo\s+(.+?)\s+Mobilização antecipada",
            r"(\d+\s*meses(?:\s*\(\d+\s*dias\))?(?:\s*ou\s*\d+\s*meses(?:\s*\(\d+\s*dias\))?)?)",
        ],
    )


def detect_minimum_amount(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Montante mínimo de constituição:\s*(EUR\s*[\d\.\,]+)",
            r"Montante mínimo[^:]*:\s*(EUR\s*[\d\.\,]+)",
            r"Mínimo[^:]*:\s*(EUR\s*[\d\.\,]+)",
        ],
    )


def detect_maximum_amount(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Montante máximo de constituição:\s*(EUR\s*[\d\.\,]+)",
            r"Montante máximo[^:]*:\s*(EUR\s*[\d\.\,]+)",
            r"Máximo[^:]*:\s*(EUR\s*[\d\.\,]+)",
        ],
    )


def detect_early_withdrawal(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Mobilização antecipada\s+(.+?)\s+Renovação",
            r"Mobilização antecipada\s+(.+?)\s+Moeda",
            r"Mobilização\s+(.+?)\s+Renovação",
        ],
    )


def detect_renewal(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Renovação\s+(.+?)\s+Moeda",
            r"Renovação\s+(.+?)\s+Montante",
            r"Renovações\s+(.+?)\s+Mobilizações",
        ],
    )


def detect_tax_regime(text: str) -> str:
    return find_first_match(
        text,
        [
            r"Regime fiscal\s+(.+?)\s+Instituição depositária",
            r"Regime fiscal\s+(.+?)\s+Garantia de capital",
            r"Residentes:\s+(.+?)\s+Não Residentes",
        ],
    )


def detect_tanb(text: str) -> str:
    matches = re.findall(
        r"(\d+,\d+%|\d+\.\d+%)",
        text,
        flags=re.IGNORECASE,
    )

    if not matches:
        return "Requires visual confirmation"

    unique_matches = []
    for match in matches:
        if match not in unique_matches:
            unique_matches.append(match)

    return "; ".join(unique_matches[:10])


def detect_document_version(text: str) -> str:
    return find_first_match(
        text,
        [
            r"(FINDP\.v\d+\.\d+)",
            r"(FIN[A-Z]*\.v\d+\.\d+)",
            r"(v\d+\.\d+)",
        ],
    )


def summarize_pdf(pdf_path: Path) -> dict:
    text = read_pdf_text(pdf_path)

    return {
        "file_name": pdf_path.name,
        "bank": detect_bank(text),
        "product": detect_product(text),
        "maturity": detect_maturity(text),
        "tanb": detect_tanb(text),
        "minimum_amount": detect_minimum_amount(text),
        "maximum_amount": detect_maximum_amount(text),
        "early_withdrawal": detect_early_withdrawal(text),
        "renewal": detect_renewal(text),
        "tax_regime": detect_tax_regime(text),
        "document_version": detect_document_version(text),
        "text_preview": text[:2500],
    }


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
            file.write(f"**Document version:** {item['document_version']}\n\n")

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
