from src.calculator import load_data, prepare_data, compare_deposits


def main():
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

    print("\nTop term deposits:\n")
    print(ranking.to_string(index=False))


if __name__ == "__main__":
    main()
