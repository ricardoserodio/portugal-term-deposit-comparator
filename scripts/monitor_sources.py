import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
import sys

import pandas as pd
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_io import read_source_links


BASE_DIR = Path(__file__).resolve().parents[1]

SOURCE_LINKS_PATH = BASE_DIR / "data" / "source_links.csv"
VALIDATION_DIR = BASE_DIR / "validation"
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
SNAPSHOT_FILE = SNAPSHOTS_DIR / "source_snapshots.json"


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def make_source_id(bank: str, product: str, url: str) -> str:
    raw = f"{bank}|{product}|{url}".lower().strip()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def make_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def load_snapshots() -> dict:
    if SNAPSHOT_FILE.exists():
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    return {}


def save_snapshots(snapshots: dict) -> None:
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as file:
        json.dump(snapshots, file, ensure_ascii=False, indent=2)


def fetch_source(url: str) -> dict:
    try:
        response = requests.get(
            url,
            timeout=25,
            headers={"User-Agent": "Mozilla/5.0"},
        )

        status_code = response.status_code
        content_type = response.headers.get("Content-Type", "").lower()

        response.raise_for_status()

        raw_bytes = response.content

        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            comparison_text = hashlib.sha256(raw_bytes).hexdigest()

            extracted_text = (
                "PDF or binary source detected. "
                "Raw content hash used for change detection. "
                "Manual review of the official document is required."
            )

        else:
            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            extracted_text = soup.get_text(separator=" ", strip=True)
            extracted_text = normalize_text(extracted_text)

            if not extracted_text:
                extracted_text = "No readable text extracted from this source."

            comparison_text = extracted_text

        comparison_text = normalize_text(comparison_text)
        current_hash = make_hash(comparison_text)

        return {
            "success": True,
            "status_code": status_code,
            "content_type": content_type,
            "current_hash": current_hash,
            "content_length": len(comparison_text),
            "extracted_text_preview": extracted_text[:4000],
            "error": "",
        }

    except Exception as e:
        return {
            "success": False,
            "status_code": "",
            "content_type": "",
            "current_hash": "",
            "content_length": 0,
            "extracted_text_preview": "",
            "error": str(e),
        }


def compare_with_snapshot(source_id: str, current_hash: str, snapshots: dict) -> str:
    if source_id not in snapshots:
        return "No previous snapshot"

    previous_hash = snapshots[source_id].get("hash", "")

    if not current_hash:
        return "Source unavailable"

    if previous_hash == current_hash:
        return "No change detected"

    return "Change detected"


def suggested_action(change_status: str) -> str:
    if change_status == "No previous snapshot":
        return "Create baseline after manual validation."

    if change_status == "No change detected":
        return "No immediate action required. Keep current validation status."

    if change_status == "Change detected":
        return (
            "Manual review required. Check TANB, maturity, minimum, maximum, "
            "eligibility and early withdrawal conditions."
        )

    if change_status == "Source unavailable":
        return "Check source manually. Do not update dataset without confirmation."

    return "Manual review required."


def generate_validation_report(accept_snapshots: bool = False) -> Path:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    sources = read_source_links(SOURCE_LINKS_PATH)
    snapshots = load_snapshots()

    active_sources = sources[
        sources["Ativo"].astype(str).str.lower().isin(["sim", "yes", "true", "1"])
    ]

    report_rows = []
    updated_snapshots = snapshots.copy()

    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for _, row in active_sources.iterrows():
        bank = str(row.get("Banco", "")).strip()
        product = str(row.get("Produto", "")).strip()
        source_type = str(row.get("Tipo Fonte", "")).strip()
        url = str(row.get("URL", "")).strip()
        fields_to_validate = str(row.get("Campo a validar", "")).strip()
        previous_audit_status = str(row.get("Estado auditoria", "")).strip()
        previous_audit_notes = str(row.get("Notas auditoria", "")).strip()

        source_id = make_source_id(bank, product, url)
        fetch_result = fetch_source(url)

        previous_hash = snapshots.get(source_id, {}).get("hash", "")

        if fetch_result["success"]:
            current_hash = fetch_result["current_hash"]

            change_status = compare_with_snapshot(
                source_id=source_id,
                current_hash=current_hash,
                snapshots=snapshots,
            )

            if accept_snapshots:
                updated_snapshots[source_id] = {
                    "bank": bank,
                    "product": product,
                    "source_type": source_type,
                    "url": url,
                    "hash": current_hash,
                    "content_length": fetch_result["content_length"],
                    "content_type": fetch_result["content_type"],
                    "last_accepted_snapshot": run_timestamp,
                }

        else:
            current_hash = ""
            change_status = "Source unavailable"

        if change_status in ["No previous snapshot", "Change detected", "Source unavailable"]:
            validation_status = "Pending human review"
        else:
            validation_status = "No change detected"

        report_rows.append(
            {
                "Detection Date": run_timestamp,
                "Bank": bank,
                "Product": product,
                "Source Type": source_type,
                "Official Link": url,
                "Fields to Validate": fields_to_validate,
                "Previous Audit Status": previous_audit_status,
                "Previous Audit Notes": previous_audit_notes,
                "Source ID": source_id,
                "Change Status": change_status,
                "Previous Snapshot Hash": previous_hash,
                "Current Source Hash": current_hash,
                "HTTP Status": fetch_result.get("status_code", ""),
                "Content Type": fetch_result.get("content_type", ""),
                "Content Length": fetch_result.get("content_length", 0),
                "Validation Status": validation_status,
                "Suggested Action": suggested_action(change_status),
                "Human Decision": "",
                "Validator Notes": "",
                "Extracted Source Text Preview": fetch_result.get("extracted_text_preview", ""),
                "Error": fetch_result.get("error", ""),
                "Snapshot Accepted This Run": "Yes" if accept_snapshots and fetch_result["success"] else "No",
            }
        )

    if accept_snapshots:
        save_snapshots(updated_snapshots)

    report = pd.DataFrame(report_rows)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = VALIDATION_DIR / f"validation_report_{timestamp}.csv"

    report.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("Validation report created successfully:")
    print(output_path)

    if accept_snapshots:
        print("Snapshot baselines updated:")
        print(SNAPSHOT_FILE)
    else:
        print("Snapshot baselines were NOT updated.")
        print("After manual validation, run:")
        print("python scripts/monitor_sources.py --accept-snapshots")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Monitor official bank sources and generate human validation reports."
    )

    parser.add_argument(
        "--accept-snapshots",
        action="store_true",
        help="Update snapshot baselines after manual validation.",
    )

    args = parser.parse_args()

    generate_validation_report(
        accept_snapshots=args.accept_snapshots,
    )


if __name__ == "__main__":
    main()
