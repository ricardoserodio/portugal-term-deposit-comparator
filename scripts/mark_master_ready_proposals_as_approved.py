import pandas as pd

MASTER_PATH = "validation/proposed_validations_ai_master.csv"


def main():
    df = pd.read_csv(MASTER_PATH, sep=";", encoding="utf-8-sig", dtype=str)

    df.columns = [str(col).strip() for col in df.columns]

    if "approve" not in df.columns:
        df["approve"] = ""

    df["approve"] = df["approve"].fillna("").astype(str)

    match_columns = [
        "tanb_match",
        "maturity_match",
        "min_amount_match",
        "max_amount_match",
        "early_withdrawal_match",
    ]

    for col in match_columns:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    mask = (
        df["tanb_match"].eq("Yes")
        & df["maturity_match"].eq("Yes")
        & df["min_amount_match"].eq("Yes")
        & df["max_amount_match"].eq("Yes")
        & df["early_withdrawal_match"].eq("Yes")
        & df["suggested_status"].isin(["Ready_for_Approval", "Partially_Validated"])
    )

    df.loc[mask, "approve"] = "Yes"

    df.to_csv(MASTER_PATH, sep=";", index=False, encoding="utf-8-sig")

    print(f"Updated file: {MASTER_PATH}")
    print(f"Rows marked as approved: {int(mask.sum())}")
    print()
    print(df[[
        "bank",
        "product",
        "suggested_status",
        "tanb_match",
        "maturity_match",
        "min_amount_match",
        "max_amount_match",
        "early_withdrawal_match",
        "approve"
    ]].to_string(index=False))


if __name__ == "__main__":
    main()