import csv
import os
from datetime import date

import pandas as pd


PROPOSALS_PATH = "validation/proposed_validations_ai.csv"
VALIDATION_LOG_PATH = "validation/bank_rate_validation_log.csv"


LOG_COLUMNS = [
    "validation_date",
    "bank",
    "product",
    "maturity_months",
    "dataset_tanb",
    "official_tanb",
    "tanb_match",
    "dataset_min_amount",
    "official_min_amount",
    "min_amount_match",
    "dataset_max_amount",
    "official_max_amount",
    "max_amount_match",
    "dataset_early_withdrawal",
    "official_early_withdrawal",
    "early_withdrawal_match",
    "source_type",
    "source_url",
    "validation_status",
    "notes",
]


def read_csv_flexible(path):
    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str)
        if len(df.columns) > 1:
            return df, ";"
    except Exception:
        pass

    df = pd.read_csv(path, sep=",", encoding="utf-8-sig", dtype=str)
    return df, ","


def normalize_value(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def normalize_approval(value):
    return normalize_value(value).lower() in ["yes", "y", "sim", "s", "true", "1"]


def choose_validation_status(row):
    suggested_status = normalize_value(row.get("suggested_status", ""))

    if suggested_status == "Ready_for_Approval":
        source_type = normalize_value(row.get("source_type", ""))
        if source_type == "Official PDF":
            return "Validated_FIN"
        return "Validated_Official_Page"

    if suggested_status in ["Partially_Validated", "Needs_Manual_Review"]:
        return suggested_status

    return suggested_status or "Partially_Validated"


def build_log_row(row):
    maturity = row.get("official_maturity_months", "")
    if normalize_value(maturity) == "":
        maturity = row.get("dataset_maturity_months", "")

    return {
        "validation_date": date.today().isoformat(),
        "bank": normalize_value(row.get("bank", "")),
        "product": normalize_value(row.get("product", "")),
        "maturity_months": normalize_value(maturity),
        "dataset_tanb": normalize_value(row.get("dataset_tanb", "")),
        "official_tanb": normalize_value(row.get("official_tanb", "")),
        "tanb_match": normalize_value(row.get("tanb_match", "")),
        "dataset_min_amount": normalize_value(row.get("dataset_min_amount", "")),
        "official_min_amount": normalize_value(row.get("official_min_amount", "")),
        "min_amount_match": normalize_value(row.get("min_amount_match", "")),
        "dataset_max_amount": normalize_value(row.get("dataset_max_amount", "")),
        "official_max_amount": normalize_value(row.get("official_max_amount", "")),
        "max_amount_match": normalize_value(row.get("max_amount_match", "")),
        "dataset_early_withdrawal": normalize_value(row.get("dataset_early_withdrawal", "")),
        "official_early_withdrawal": normalize_value(row.get("official_early_withdrawal", "")),
        "early_withdrawal_match": normalize_value(row.get("early_withdrawal_match", "")),
        "source_type": normalize_value(row.get("source_type", "")),
        "source_url": normalize_value(row.get("source_url", "")),
        "validation_status": choose_validation_status(row),
        "notes": normalize_value(row.get("evidence_summary", "")),
    }


def make_key(row):
    return (
        normalize_value(row.get("bank", "")).lower(),
        normalize_value(row.get("product", "")).lower(),
        normalize_value(row.get("maturity_months", "")).lower(),
        normalize_value(row.get("dataset_tanb", "")).lower(),
        normalize_value(row.get("official_tanb", "")).lower(),
        normalize_value(row.get("source_url", "")).lower(),
    )


def existing_log_keys():
    if not os.path.exists(VALIDATION_LOG_PATH) or os.path.getsize(VALIDATION_LOG_PATH) == 0:
        return set()

    existing, _ = read_csv_flexible(VALIDATION_LOG_PATH)

    keys = set()
    for _, row in existing.iterrows():
        keys.add(make_key(row))

    return keys


def append_rows_to_log(log_rows):
    file_exists = os.path.exists(VALIDATION_LOG_PATH) and os.path.getsize(VALIDATION_LOG_PATH) > 0

    with open(VALIDATION_LOG_PATH, "a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=LOG_COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerows(log_rows)


def main():
    proposals, _ = read_csv_flexible(PROPOSALS_PATH)
    proposals.columns = [str(col).strip() for col in proposals.columns]

    if "approve" not in proposals.columns:
        raise ValueError("Column 'approve' not found in proposals file.")

    approved = proposals[proposals["approve"].apply(normalize_approval)].copy()

    if approved.empty:
        print("No approved rows found. Write Yes in the approve column first.")
        return

    existing_keys = existing_log_keys()
    log_rows = []
    skipped_duplicates = 0

    for _, row in approved.iterrows():
        log_row = build_log_row(row)
        key = make_key(log_row)

        if key in existing_keys:
            skipped_duplicates += 1
            continue

        log_rows.append(log_row)
        existing_keys.add(key)

    if not log_rows:
        print("No new rows to add.")
        print(f"Skipped duplicates: {skipped_duplicates}")
        return

    append_rows_to_log(log_rows)

    print(f"Approved rows added to: {VALIDATION_LOG_PATH}")
    print(f"Rows added: {len(log_rows)}")
    print(f"Skipped duplicates: {skipped_duplicates}")


if __name__ == "__main__":
    main()