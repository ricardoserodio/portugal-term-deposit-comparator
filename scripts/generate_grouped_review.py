from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

VALIDATION_DIR = BASE_DIR / "validation"
REVIEW_REQUIRED_PATH = VALIDATION_DIR / "review_required.csv"
OUTPUT_PATH = VALIDATION_DIR / "grouped_validation_review.md"


def clean_value(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def main():
    if not REVIEW_REQUIRED_PATH.exists():
        raise FileNotFoundError(
            "review_required.csv not found. Run first:\n"
            "python scripts/monitor_sources.py\n"
            "python scripts/validation_summary.py"
        )

    df = pd.read_csv(REVIEW_REQUIRED_PATH)

    required_columns = [
        "Traffic Light",
        "Bank",
        "Product",
        "Source Type",
        "Change Status",
        "Official Link",
        "Fields to Validate",
        "Suggested Action",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Missing required columns in review_required.csv: {missing_columns}"
        )

    grouped = df.groupby(
        ["Bank", "Product", "Source Type", "Official Link"],
        dropna=False,
    )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("# Grouped Validation Review\n\n")
        f.write(
            "This document groups validation items by product and official source, "
            "so each product/source appears only once.\n\n"
        )
        f.write("---\n\n")

        counter = 1

        for (bank, product, source_type, official_link), group in grouped:
            traffic_lights = sorted(set(group["Traffic Light"].dropna().astype(str)))
            change_statuses = sorted(set(group["Change Status"].dropna().astype(str)))
            fields = sorted(set(group["Fields to Validate"].dropna().astype(str)))
            suggested_actions = sorted(set(group["Suggested Action"].dropna().astype(str)))

            f.write(f"## {counter}. {clean_value(bank)} — {clean_value(product)}\n\n")

            f.write(f"**Source Type:** {clean_value(source_type)}\n\n")
            f.write(f"**Traffic Light:** {'; '.join(traffic_lights)}\n\n")
            f.write(f"**Change Status:** {'; '.join(change_statuses)}\n\n")

            f.write("**Fields to Validate:**\n\n")
            for field_group in fields:
                split_fields = [
                    item.strip()
                    for item in str(field_group).replace(",", ";").split(";")
                    if item.strip()
                ]

                for field in split_fields:
                    f.write(f"- {field}\n")

            f.write("\n")

            f.write(f"**Official Link:** {clean_value(official_link)}\n\n")

            f.write("**Suggested Action:**\n\n")
            for action in suggested_actions:
                f.write(f"- {clean_value(action)}\n")

            f.write("\n")

            f.write("**Official Values Confirmed:**\n\n")
            f.write("- TANB: \n")
            f.write("- Maturity / Prazo: \n")
            f.write("- Minimum Amount / Montante mínimo: \n")
            f.write("- Maximum Amount / Montante máximo: \n")
            f.write("- Early Withdrawal / Mobilização antecipada: \n")
            f.write("- Renewal / Renovação: \n")
            f.write("- Other notes / Outras notas: \n\n")

            f.write("**Human Decision:** \n\n")
            f.write("Use one of: `Validated`, `Update dataset`, `Keep under review`, `Source unavailable`\n\n")

            f.write("**Validator Notes:** \n\n")

            f.write("---\n\n")

            counter += 1

    print("\nGROUPED VALIDATION REVIEW CREATED")
    print("=" * 70)
    print(f"File: {OUTPUT_PATH}")
    print(f"Products/sources grouped: {counter - 1}")
    print("=" * 70)
    print("\nOpen it with:")
    print("code validation/grouped_validation_review.md")


if __name__ == "__main__":
    main()
