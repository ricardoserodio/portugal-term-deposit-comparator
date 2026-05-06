from pathlib import Path

import pandas as pd


SOURCE_LINKS_PATH = Path("data/source_links.csv")


def read_source_links(path=SOURCE_LINKS_PATH) -> pd.DataFrame:
    """Read the official source links mapping file."""
    return pd.read_csv(
        path,
        sep="|",
        encoding="utf-8-sig",
        dtype=str,
    )
