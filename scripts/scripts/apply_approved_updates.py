from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

DATASET_PATH = BASE_DIR / "data" / "depositos_prazo_core_portugal_corrigido.csv"
VALIDATION_DIR = BASE_DIR / "validation"
PROPOSED_UPDATES_PATH = VALIDATION_DIR / "proposed_updates.csv"
BACKUP_DIR = BASE_DIR / "outputs" / "dataset_backups"


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None


def normalize_approval(value: str) -> str:
    return str(value).strip().lower()


def should_apply(value: str) -> bool:
    return normalize_approval(value) in ["approve", "approved", "aprovado", "aprovar"]


def create_backup() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"depositos_prazo_core_portugal_corrigido_backup_{timestamp}.csv"

    dataset = pd.read_csv(DATASET_PATH)
    dataset.to_csv(backup_path, index=False, encoding="utf-8-sig")

    return backup_path


def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    if not PROPOSED_UPDATES_PATH.exists():
        raise FileNotFoundError(
            "proposed_updates.csv not found. Run first:\n"
            "python scripts/propose_dataset_updates.py"
        )

    dataset = pd.read_csv(DATASET_PATH)
    updates = pd.read_csv(PROPOSED_UPDATES_PATH, sep="|")

    approved_updates = updates[updates["Human Approval"].apply(should_apply)].copy()

    if approved_updates.empty:
        print("\nNo approved updates found.")
        print("Fill 'Human Approval' with 'Approve' for rows you want to apply.")
        return

    backup_path = create_backup()

    applied_rows = []
    skipped_rows = []

    for _, row in approved_updates.iterrows():
        bank = str(row.get("Bank", "")).strip()
        product = str(row.get("Product", "")).strip()
        dataset_column = str(row.get("Dataset Column", "")).strip()
        new_value = row.get("Detected Official Value", "")
        row_index = row.get("Dataset Row Index", "")

        if not dataset_column or dataset_column not in dataset.columns:
            skipped_rows.append(
                {
                    "Bank": bank,
                    "Product": product,
                    "Field": row.get("Field", ""),
                    "Reason": "Dataset column not found",
                }
            )
            continue

        if pd.isna(new_value) or str(new_value).strip() == "":
            skipped_rows.append(
                {
                    "Bank": bank,
                    "Product": product,
                    "Field": row.get("Field", ""),
                    "Reason": "Detected Official Value is empty",
                }
            )
            continue

        try:
            row_index_int = int(row_index)
        except Exception:
            skipped_rows.append(
                {
                    "Bank": bank,
                    "Product": product,
                    "Field": row.get("Field", ""),
                    "Reason": "Dataset Row Index invalid",
                }
            )
            continue

        if row_index_int not in dataset.index:
            skipped_rows.append(
                {
                    "Bank": bank,
                    "Product": product,
                    "Field": row.get("Field", ""),
                    "Reason": "Dataset row index not found",
                }
            )
            continue

        old_value = dataset.at[row_index_int, dataset_column]
        dataset.at[row_index_int, dataset_column] = new_value

        applied_rows.append(
            {
                "Bank": bank,
                "Product": product,
                "Dataset Row Index": row_index_int,
                "Dataset Column": dataset_column,
                "Old Value": old_value,
                "New Value": new_value,
                "Validator Notes": row.get("Validator Notes", ""),
            }
        )

    dataset.to_csv(DATASET_PATH, index=False, encoding="utf-8-sig")

    applied_report_path = VALIDATION_DIR / "applied_updates_report.csv"
    skipped_report_path = VALIDATION_DIR / "skipped_updates_report.csv"

    pd.DataFrame(applied_rows).to_csv(applied_report_path, index=False, encoding="utf-8-sig")
    pd.DataFrame(skipped_rows).to_csv(skipped_report_path, index=False, encoding="utf-8-sig")

    print("\nMANUAL APPROVED UPDATES APPLIED")
    print("=" * 70)
    print(f"Backup created: {backup_path}")
    print(f"Dataset updated: {DATASET_PATH}")
    print(f"Applied updates: {len(applied_rows)}")
    print(f"Skipped updates: {len(skipped_rows)}")
    print("=" * 70)

    if applied_rows:
        print("\nApplied:")
        for item in applied_rows:
            print(
                f"- {item['Bank']} | {item['Product']} | "
                f"{item['Dataset Column']}: {item['Old Value']} -> {item['New Value']}"
            )

    if skipped_rows:
        print("\nSkipped:")
        for item in skipped_rows:
            print(
                f"- {item['Bank']} | {item['Product']} | "
                f"{item['Field']} | {item['Reason']}"
            )

    print("\nNext steps:")
    print("1. Run the Streamlit app and confirm the values look correct.")
    print("2. If everything is correct, accept the source baseline:")
    print("   python scripts/monitor_sources.py --accept-snapshots")
    print("3. Commit the updated dataset and validation reports if needed.")


if __name__ == "__main__":
    main()
