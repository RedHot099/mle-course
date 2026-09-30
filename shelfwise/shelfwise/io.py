"""Reading invoice lines and building the product catalogue."""

from pathlib import Path

import pandas as pd

LINE_COLUMNS = [
    "invoice",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "price",
    "customer_id",
    "country",
]

# Rough product families from words in the description. Good enough for
# the category view of the report; anything else is OTHER.
CATEGORY_WORDS = {
    "LIGHT": "LIGHTS",
    "CANDLE": "CANDLES",
    "BAG": "BAGS",
    "MUG": "KITCHEN",
    "CAKE": "KITCHEN",
    "TEA": "KITCHEN",
    "CARD": "PAPER",
    "WRAP": "PAPER",
    "SIGN": "DECOR",
    "HEART": "DECOR",
    "CHRISTMAS": "SEASONAL",
}


def read_lines(path: Path) -> pd.DataFrame:
    """Read the invoice lines cache written by the data team (parquet)."""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Build it first (see README, 'Dane').")
    lines = pd.read_parquet(path, columns=LINE_COLUMNS)
    lines["stock_code"] = lines["stock_code"].str.strip().str.upper()
    return lines


def category_of(description: str) -> str:
    text = str(description).upper()
    for word, category in CATEGORY_WORDS.items():
        if word in text:
            return category
    return "OTHER"


def build_catalogue(lines: pd.DataFrame) -> pd.DataFrame:
    """One row per product: code, description and category."""
    # >>> SOLUTION 17.8
    named = lines.dropna(subset=["description"])
    # A code has several spellings of its description over the years; keep
    # the most frequent one, so every code appears exactly once.
    description = (
        named.groupby("stock_code")["description"]
        .agg(lambda texts: texts.value_counts().index[0])
        .reset_index()
    )
    catalogue = description
    # --- STUB
    #| catalogue = lines[["stock_code", "description"]].dropna().drop_duplicates()
    # <<< SOLUTION
    catalogue["category"] = catalogue["description"].map(category_of)
    return catalogue.reset_index(drop=True)
