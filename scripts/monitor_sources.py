import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

SOURCE_LINKS_PATH = BASE_DIR / "data" / "source_links.csv"
VALIDATION_DIR = BASE_DIR / "validation"


def fetch_page_text(url: str) -> str:
    """
    Reads basic text from an official source.

    This script does not update the validated dataset.
    It only supports human review.
    """
    try:
        response = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if not text:
            return "No readable text extracted from this source."

        return text[:4000]

    except Exception as e:
        return f"ERROR READING SOURCE: {e}"


def generate_validation_report():
    """
    Generates a human validation report from official source links.

    Important:
    This script does NOT change the main dataset.
    The final deposit dataset must only be updated after manual validation.
    """
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    sources = pd.read_csv(SOURCE_LINKS_PATH, sep="|")

    active_sources = sources[
        sources["Ativo"].astype(str).str.lower().isin(["sim", "yes", "true", "1"])
    ]

    report_rows = []

    for _, row in active_sources.iterrows():
        banco = row.get("Banco", "")
        produto = row.get("Produto", "")
        tipo_fonte = row.get("Tipo Fonte", "")
        url = row.get("URL", "")
        campo = row.get("Campo a validar", "")
        estado_auditoria = row.get("Estado auditoria", "")
        notas_auditoria = row.get("Notas auditoria", "")

        page_text = fetch_page_text(url)

        report_rows.append({
            "Detection Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Bank": banco,
            "Product": produto,
            "Source Type": tipo_fonte,
            "Official Link": url,
            "Fields to Validate": campo,
            "Previous Audit Status": estado_auditoria,
            "Previous Audit Notes": notas_auditoria,
            "Extracted Source Text": page_text,
            "Validation Status": "Pending human review",
            "Human Decision": "",
            "Suggested Action": "Manually validate TANB, term, minimum, maximum, eligibility and early withdrawal conditions.",
            "Validator Notes": ""
        })

    report = pd.DataFrame(report_rows)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = VALIDATION_DIR / f"validation_report_{timestamp}.csv"

    report.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("Validation report created successfully:")
    print(output_path)


if __name__ == "__main__":
    generate_validation_report()