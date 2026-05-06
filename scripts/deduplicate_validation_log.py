import pandas as pd

VALIDATION_LOG_PATH = "validation/bank_rate_validation_log.csv"


def read_csv_flexible(path):
    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str)
        if len(df.columns) > 1:
            return df, ";"
    except Exception:
        pass

    df = pd.read_csv(path, sep=",", encoding="utf-8-sig", dtype=str)
    return df, ","


def main():
    df, sep = read_csv_flexible(VALIDATION_LOG_PATH)

    before = len(df)

    key_columns = [
        "bank",
        "product",
        "maturity_months",
        "dataset_tanb",
        "official_tanb",
        "source_url",
    ]

    existing_key_columns = [col for col in key_columns if col in df.columns]

    if not existing_key_columns:
        raise ValueError("No matching key columns found for deduplication.")

    df = df.drop_duplicates(subset=existing_key_columns, keep="first")

    after = len(df)

    df.to_csv(VALIDATION_LOG_PATH, index=False, sep=sep, encoding="utf-8-sig")

    print(f"Validation log cleaned: {VALIDATION_LOG_PATH}")
    print(f"Rows before: {before}")
    print(f"Rows after: {after}")
    print(f"Duplicates removed: {before - after}")


if __name__ == "__main__":
    main()