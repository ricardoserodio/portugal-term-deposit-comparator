import pandas as pd

DATASET_PATH = "data/depositos_prazo_core_portugal_corrigido.csv"

def main():
    df = pd.read_csv(DATASET_PATH)

    before = len(df)

    mask = ~(
        df.iloc[:, 0].astype(str).str.strip().eq("Banco BiG")
        & df.iloc[:, 1].astype(str).str.strip().eq("Depósito ON")
    )

    df_clean = df[mask].copy()

    after = len(df_clean)

    df_clean.to_csv(DATASET_PATH, index=False, encoding="utf-8-sig")

    print(f"Dataset updated: {DATASET_PATH}")
    print(f"Rows before: {before}")
    print(f"Rows after: {after}")
    print(f"Rows removed: {before - after}")

if __name__ == "__main__":
    main()