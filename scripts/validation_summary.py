from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
VALIDATION_DIR = BASE_DIR / "validation"


GREEN_STATUSES = ["No change detected"]
YELLOW_STATUSES = ["No previous snapshot"]
RED_STATUSES = ["Change detected", "Source unavailable", "Extraction failed"]


def get_latest_validation_report() -> Path:
    reports = sorted(
        VALIDATION_DIR.glob("validation_report_*.csv"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not reports:
        raise FileNotFoundError(
            "No validation reports found. Run first: python scripts/monitor_sources.py"
        )

    return reports[0]


def classify_status(status: str) -> str:
    status = str(status).strip()

    if status in GREEN_STATUSES:
        return "GREEN"

    if status in YELLOW_STATUSES:
        return "YELLOW"

    if status in RED_STATUSES:
        return "RED"

    return "RED"


def decision_text(green_count: int, yellow_count: int, red_count: int) -> str:
    if red_count > 0:
        return "MANUAL REVIEW REQUIRED"

    if yellow_count > 0:
        return "BASELINE REVIEW REQUIRED"

    return "VALIDATION PASSED"


def main():
    latest_report = get_latest_validation_report()

    df = pd.read_csv(latest_report)

    if "Change Status" not in df.columns:
        raise ValueError(
            "The latest validation report does not contain a 'Change Status' column."
        )

    df["Traffic Light"] = df["Change Status"].apply(classify_status)

    green_count = (df["Traffic Light"] == "GREEN").sum()
    yellow_count = (df["Traffic Light"] == "YELLOW").sum()
    red_count = (df["Traffic Light"] == "RED").sum()
    total = len(df)

    decision = decision_text(green_count, yellow_count, red_count)

    print("\nVALIDATION SUMMARY")
    print("=" * 70)
    print(f"Latest report: {latest_report.name}")
    print(f"Total sources checked: {total}")
    print("-" * 70)
    print(f"GREEN  | {green_count} | No change detected")
    print(f"YELLOW | {yellow_count} | No previous snapshot / baseline needed")
    print(f"RED    | {red_count} | Change detected or source issue")
    print("=" * 70)
    print(f"DECISION: {decision}")
    print("=" * 70)

    review_df = df[df["Traffic Light"].isin(["YELLOW", "RED"])].copy()

    review_columns = [
        "Traffic Light",
        "Bank",
        "Product",
        "Source Type",
        "Change Status",
        "Official Link",
        "Fields to Validate",
        "Previous Audit Status",
        "Previous Audit Notes",
        "Suggested Action",
        "Human Decision",
        "Validator Notes",
        "Error",
    ]

    available_columns = [col for col in review_columns if col in review_df.columns]
    review_df = review_df[available_columns]

    review_output_path = VALIDATION_DIR / "review_required.csv"
    full_summary_output_path = VALIDATION_DIR / "latest_validation_summary.csv"

    df.to_csv(full_summary_output_path, index=False, encoding="utf-8-sig")
    review_df.to_csv(review_output_path, index=False, encoding="utf-8-sig")

    if review_df.empty:
        print("\nNo manual review items found.")
        print("Everything is GREEN.")
        print("\nYou do not need to update snapshots unless you intentionally want to refresh the baseline.")
    else:
        print("\nITEMS REQUIRING REVIEW")
        print("-" * 70)

        for _, row in review_df.iterrows():
            print(f"{row.get('Traffic Light', '')} | {row.get('Bank', '')} | {row.get('Product', '')}")
            print(f"Status: {row.get('Change Status', '')}")
            print(f"Fields to validate: {row.get('Fields to Validate', '')}")
            print(f"Link: {row.get('Official Link', '')}")
            print(f"Suggested action: {row.get('Suggested Action', '')}")
            print("-" * 70)

        print("\nOpen this file to validate directly:")
        print(review_output_path)

        print("\nHow to validate:")
        print("1. Open each Official Link.")
        print("2. Check the fields listed in 'Fields to Validate'.")
        print("3. Fill 'Human Decision' with one of:")
        print("   - Validated")
        print("   - Update dataset")
        print("   - Keep under review")
        print("   - Source unavailable")
        print("4. Add short notes in 'Validator Notes'.")
        print("5. If all reviewed sources are accepted, run:")
        print("   python scripts/monitor_sources.py --accept-snapshots")

    print("\nDetailed files exported:")
    print(f"- {full_summary_output_path}")
    print(f"- {review_output_path}")


if __name__ == "__main__":
    main()
