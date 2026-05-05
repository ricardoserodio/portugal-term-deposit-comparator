import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

DATASET_PATH = BASE_DIR / "data" / "depositos_prazo_core_portugal_corrigido.csv"
VALIDATION_DIR = BASE_DIR / "validation"
REVIEW_REQUIRED_PATH = VALIDATION_DIR / "review_required.csv"
OUTPUT_PATH = VALIDATION_DIR / "proposed_updates.csv"


FIELD_TO_DATASET_CANDIDATES = {
    "TANB": ["TANB", "TANB (%)", "Taxa", "Taxa TANB"],
    "Maturity": ["Prazo (meses)", "Prazo", "Maturity", "Maturity (months)"],
    "Minimum Amount": ["Montante mínimo", "Minimo", "Mínimo", "Minimum investment", "Minimum Amount"],
    "Maximum Amount": ["Montante máximo", "Maximo", "Máximo", "Maximum investment", "Maximum Amount"],
    "Early Withdrawal": ["Mobilização antecipada", "Early withdrawal", "Early Withdrawal"],
    "Renewal": ["Renovação", "Renewal"],
    "Notes": ["Notas / condições", "Notas", "Notes", "Conditions"],
    "Official Source": ["Fonte oficial / referência", "Fonte oficial", "Official source", "Source"],
    "Validation Status": ["Estado de validação", "Validation status", "Validation Status"],
    "Reference Date": ["Data de referência", "Reference date", "Reference Date"],
}


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None


def detect_dataset_columns(df: pd.DataFrame) -> dict:
    return {
        "bank": find_column(df, ["Banco", "Bank"]),
        "product": find_column(df, ["Produto", "Product"]),
        "maturity": find_column(df, ["Prazo (meses)", "Prazo", "Maturity", "Maturity (months)"]),
    }


def split_fields(fields_text: str) -> list[str]:
    if pd.isna(fields_text):
        return []

    raw_fields = re.split(r"[;,]", str(fields_text))
    fields = []

    for field in raw_fields:
        clean = field.strip()
        if clean:
            fields.append(clean)

    return fields


def normalize_field_name(field: str) -> str:
    field_lower = field.lower().strip()

    if "tanb" in field_lower or "taxa" in field_lower:
        return "TANB"

    if "prazo" in field_lower or "maturity" in field_lower:
        return "Maturity"

    if "mínimo" in field_lower or "minimo" in field_lower or "minimum" in field_lower:
        return "Minimum Amount"

    if "máximo" in field_lower or "maximo" in field_lower or "maximum" in field_lower:
        return "Maximum Amount"

    if "mobil" in field_lower or "early" in field_lower:
        return "Early Withdrawal"

    if "renova" in field_lower or "renew" in field_lower:
        return "Renewal"

    if "nota" in field_lower or "condition" in field_lower:
        return "Notes"

    return field.strip()


def get_dataset_value(
    dataset: pd.DataFrame,
    bank: str,
    product: str,
    maturity: str | None,
    field: str,
    dataset_columns: dict,
):
    bank_col = dataset_columns.get("bank")
    product_col = dataset_columns.get("product")
    maturity_col = dataset_columns.get("maturity")

    if not bank_col or not product_col:
        return "", None, None

    mask = (
        dataset[bank_col].astype(str).str.strip().eq(str(bank).strip())
        & dataset[product_col].astype(str).str.strip().eq(str(product).strip())
    )

    if maturity and maturity_col and str(maturity).strip():
        mask = mask & dataset[maturity_col].astype(str).str.strip().eq(str(maturity).strip())

    matches = dataset[mask]

    target_col = find_column(dataset, FIELD_TO_DATASET_CANDIDATES.get(field, [field]))

    if matches.empty:
        return "", target_col, None

    if target_col is None:
        return "", None, matches.index[0]

    return matches.iloc[0].get(target_col, ""), target_col, matches.index[0]


def main():
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    if not REVIEW_REQUIRED_PATH.exists():
        raise FileNotFoundError(
            "review_required.csv not found. Run first:\n"
            "python scripts/monitor_sources.py\n"
            "python scripts/validation_summary.py"
        )

    dataset = pd.read_csv(DATASET_PATH)
    review = pd.read_csv(REVIEW_REQUIRED_PATH)

    dataset_columns = detect_dataset_columns(dataset)

    proposal_rows = []

    for _, review_row in review.iterrows():
        bank = str(review_row.get("Bank", "")).strip()
        product = str(review_row.get("Product", "")).strip()
        source_type = str(review_row.get("Source Type", "")).strip()
        change_status = str(review_row.get("Change Status", "")).strip()
        official_link = str(review_row.get("Official Link", "")).strip()
        fields_to_validate = str(review_row.get("Fields to Validate", "")).strip()
        suggested_action = str(review_row.get("Suggested Action", "")).strip()

        fields = split_fields(fields_to_validate)

        if not fields:
            fields = ["TANB", "Maturity", "Minimum Amount", "Maximum Amount", "Early Withdrawal", "Renewal"]

        for field in fields:
            normalized_field = normalize_field_name(field)

            current_value, dataset_column, dataset_row_index = get_dataset_value(
                dataset=dataset,
                bank=bank,
                product=product,
                maturity=None,
                field=normalized_field,
                dataset_columns=dataset_columns,
            )

            if dataset_column:
                confidence = "Medium"
                suggested_decision = "Needs review"
            else:
                confidence = "Low"
                suggested_decision = "Needs review"

            proposal_rows.append(
                {
                    "Bank": bank,
                    "Product": product,
                    "Maturity": "",
                    "Field": normalized_field,
                    "Dataset Column": dataset_column or "",
                    "Dataset Row Index": "" if dataset_row_index is None else dataset_row_index,
                    "Current Dataset Value": current_value,
                    "Detected Official Value": "",
                    "Confidence": confidence,
                    "Change Status": change_status,
                    "Source Type": source_type,
                    "Official Link": official_link,
                    "Suggested Action": suggested_action,
                    "Suggested Decision": suggested_decision,
                    "Human Approval": "",
                    "Validator Notes": "",
                }
            )

    proposals = pd.DataFrame(proposal_rows)
    proposals.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig", sep="|")

    print("\nPROPOSED UPDATES TEMPLATE CREATED")
    print("=" * 70)
    print(f"File: {OUTPUT_PATH}")
    print(f"Rows created: {len(proposals)}")
    print("=" * 70)
    print("\nWhat to do next:")
    print("1. Open validation/proposed_updates.csv")
    print("2. Fill 'Detected Official Value' with the value confirmed in the official source")
    print("3. Fill 'Human Approval' with one of:")
    print("   - Approve")
    print("   - Reject")
    print("   - Needs review")
    print("4. Add short notes in 'Validator Notes'")
    print("5. Run: python scripts/apply_approved_updates.py")


if __name__ == "__main__":
    main()
