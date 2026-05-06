import argparse
import os
import pandas as pd

from ai_propose_all_validations import (
    DATASET_PATH,
    SOURCE_LINKS_PATH,
    process_row,
)


OUTPUT_PATH = "validation/proposed_validations_ai_master.csv"


def read_existing_master(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return pd.DataFrame()

    try:
        return pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str)
    except Exception:
        return pd.read_csv(path, sep=",", encoding="utf-8-sig", dtype=str)


def make_key(row):
    return (
        str(row.get("bank", "")).strip().lower(),
        str(row.get("product", "")).strip().lower(),
        str(row.get("dataset_maturity_months", "")).strip().lower(),
        str(row.get("dataset_tanb", "")).strip().lower(),
        str(row.get("source_url", "")).strip().lower(),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bank",
        type=str,
        required=True,
        help="Bank name filter."
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.5,
        help="Seconds to wait between calls."
    )

    args = parser.parse_args()

    dataset = pd.read_csv(DATASET_PATH)
    source_links = pd.read_csv(SOURCE_LINKS_PATH, sep="|", encoding="utf-8-sig", dtype=str)

    dataset = dataset[
        dataset.iloc[:, 0].astype(str).str.contains(args.bank, case=False, na=False)
    ]

    print(f"\nRows to process: {len(dataset)}")
    print(f"Output master file: {OUTPUT_PATH}")

    if len(dataset) == 0:
        print("No dataset rows found for this bank.")
        return

    confirm = input("\nThis will call the OpenAI API for each row. Type YES to continue: ").strip()

    if confirm != "YES":
        print("Cancelled.")
        return

    existing = read_existing_master(OUTPUT_PATH)
    existing_keys = set()

    if not existing.empty:
        for _, row in existing.iterrows():
            existing_keys.add(make_key(row))

    new_rows = []
    skipped_duplicates = 0

    for index, selected_row in dataset.iterrows():
        bank = selected_row.iloc[0]
        product = selected_row.iloc[1]

        print("\n" + "=" * 80)
        print(f"Processing row {index + 1}: {bank} | {product}")

        proposal = process_row(selected_row, source_links)
        key = make_key(proposal)

        print(f"Suggested status: {proposal['suggested_status']}")
        print(f"TANB match: {proposal['tanb_match']}")
        print(f"Maturity match: {proposal['maturity_match']}")
        print(f"Min match: {proposal['min_amount_match']}")
        print(f"Max match: {proposal['max_amount_match']}")
        print(f"Early withdrawal match: {proposal['early_withdrawal_match']}")
        print(f"Source used: {proposal['source_url'] if proposal['source_url'] else 'none'}")

        if proposal["error_message"]:
            print(f"Error/message: {proposal['error_message']}")

        if key in existing_keys:
            skipped_duplicates += 1
            print("Skipped: already exists in master proposals.")
            continue

        new_rows.append(proposal)
        existing_keys.add(key)

    if not new_rows:
        print("\nNo new proposals added.")
        print(f"Skipped duplicates: {skipped_duplicates}")
        return

    new_df = pd.DataFrame(new_rows)

    if existing.empty:
        final = new_df
    else:
        final = pd.concat([existing, new_df], ignore_index=True)

    final.to_csv(OUTPUT_PATH, sep=";", index=False, encoding="utf-8-sig")

    print("\nFinished.")
    print(f"New proposals added: {len(new_rows)}")
    print(f"Skipped duplicates: {skipped_duplicates}")
    print(f"Master proposals written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()