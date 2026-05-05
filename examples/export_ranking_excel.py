from pathlib import Path

from src.calculator import load_data, prepare_data, compare_deposits


OUTPUT_DIR = Path("outputs")
OUTPUT_FILE = OUTPUT_DIR / "ranking_output.xlsx"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = load_data()
    df = prepare_data(df)

    ranking = compare_deposits(
        df=df,
        capital=10000,
        maturity_months=12,
        require_early_withdrawal=False,
        accept_new_clients_only=True,
        accept_new_money_only=True,
        top_n=10,
    )

    ranking.to_excel(OUTPUT_FILE, index=False)

    print("\nTop term deposits:\n")
    print(ranking.to_string(index=False))
    print(f"\nRanking exported to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
