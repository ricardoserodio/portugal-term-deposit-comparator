import pandas as pd

PROPOSALS_PATH = "validation/proposed_validations_ai.csv"


def read_csv_flexible(path):
    # Try semicolon first, for Portuguese Excel-compatible CSVs
    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str)
        if len(df.columns) > 1:
            return df, ";"
    except Exception:
        pass

    # Fallback to comma-separated CSV
    df = pd.read_csv(path, sep=",", encoding="utf-8-sig", dtype=str)
    return df, ","


def main():
    df, sep = read_csv_flexible(PROPOSALS_PATH)

    # Clean column names
    df.columns = [str(col).strip() for col in df.columns]

    if "approve" not in df.columns:
        df["approve"] = ""

    # Force approve column to text/object
    df["approve"] = df["approve"].fillna("").astype(str)

    if "suggested_status" not in df.columns:
        raise ValueError("Column 'suggested_status' not found in proposals file.")

    mask = df["suggested_status"].fillna("").astype(str).str.strip().eq("Ready_for_Approval")

    df.loc[mask, "approve"] = "Yes"

    df.to_csv(PROPOSALS_PATH, index=False, sep=sep, encoding="utf-8-sig")

    print(f"Updated file: {PROPOSALS_PATH}")
    print(f"Rows marked as approved: {int(mask.sum())}")
    print(f"CSV separator used: {sep}")


if __name__ == "__main__":
    main()