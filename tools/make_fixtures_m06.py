"""Build the fixtures that the module 06 checks run on. Author-only tool.

Run from the repository root after `course data`:

    uv run python tools/make_fixtures_m06.py

It reads the real workbook once (about half a minute) and writes two files
to `src/coursekit/fixtures/`:

- `online_retail_sample.xlsx`: a few dozen rows in the two-sheet layout of the
  original, with the cell types of the original (invoice numbers and stock
  codes as numbers or text, lowercase codes, empty descriptions and customer
  ids). It exercises task 06.1.
- `online_retail_sample.parquet`: about a thousand rows in the format of the
  cache written by `build_cache`. Whole invoices are picked for each kind of
  anomaly the checks rely on, plus every line of a few products, so the daily
  table has many days per product.

Nothing is random: every pick is the first few matches in sorted order, so a
run gives the same rows and the same bytes.
"""

import io
import re
import zipfile
from pathlib import Path

import pandas as pd

from coursekit import paths

XLSX_OUT = paths.FIXTURES_DIR / "online_retail_sample.xlsx"
PARQUET_OUT = paths.FIXTURES_DIR / "online_retail_sample.parquet"

HEADERS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]
NAMES = [
    "invoice",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "price",
    "customer_id",
    "country",
]
PRODUCT_CODE = r"\d{5}[A-Z]{0,2}"

# One small invoice for each of these non-product codes (canonical spelling).
NON_PRODUCT_CODES = [
    "POST",
    "DOT",
    "M",
    "C2",
    "D",
    "S",
    "BANK CHARGES",
    "ADJUST",
    "ADJUST2",
    "AMAZONFEE",
    "CRUK",
    "B",
    "PADS",
    "TEST001",
    "C3",
    "SP1002",
    "DCGS0058",
    "DCGSSGIRL",
    "GIFT_0001_20",
]
# Invoices taken by number: the one cancellation with a positive quantity and
# the one line whose stock code has a trailing space.
POSITIVE_CANCELLATION = "C496350"
TRAILING_SPACE_INVOICE = "514532"

SMALL_INVOICE = 4  # at most this many lines per copy of an invoice
HISTORY_LINES = (120, 180)  # lines of a history product, both sheets together
HISTORY_MIN_RETURNS = 8
N_HISTORY_PRODUCTS = 6
XLSX_HEAD_ROWS = 15
# openpyxl stamps the current time into the archive twice: on every member and
# in the document properties. Both are replaced with a fixed value.
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
FIXED_STAMP = b"2011-12-09T12:50:00Z"
STAMPED_PROPERTY = re.compile(rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*")


def read_original() -> pd.DataFrame:
    """Read both sheets as they are stored, one frame with a `sheet` column."""
    sheets = pd.read_excel(paths.ONLINE_RETAIL, sheet_name=None)
    frames = [frame.assign(sheet=name) for name, frame in sheets.items()]
    return pd.concat(frames, ignore_index=True)


def type_rows(original: pd.DataFrame) -> pd.DataFrame:
    """Type the rows as the cache does. Row order stays the file order."""
    typed = original.rename(columns=dict(zip(HEADERS, NAMES, strict=True)))
    typed = typed.astype(
        {
            "invoice": "str",
            "stock_code": "str",
            "description": "str",
            "customer_id": "Int64",
            "country": "str",
        }
    )
    return typed.assign(stock_code=typed["stock_code"].str.strip().str.upper())


def pick_small(
    rows: pd.DataFrame, lines: pd.Series, mask: pd.Series, count: int, cap: int
) -> list[str]:
    """Return the first `count` invoice numbers, sorted, with a row in `mask`.

    `lines` holds the number of lines per invoice; only invoices with at most
    `cap` lines qualify, so the sample stays small.
    """
    holding = rows.loc[mask, "invoice"].unique()
    fitting = lines.loc[lines.index.isin(holding) & (lines <= cap)]
    return sorted(fitting.index)[:count]


def pick_invoices(rows: pd.DataFrame) -> set[str]:
    """Choose whole invoices, one group per anomaly the checks use."""
    # Lines per copy of an invoice: a copy in each sheet counts once.
    lines = rows.groupby(["sheet", "invoice"]).size().groupby("invoice").max()
    sheets = rows.groupby("invoice")["sheet"].nunique()
    in_overlap = rows["invoice"].isin(sheets.index[sheets > 1])
    repeated = rows.duplicated([*NAMES, "sheet"])
    has_repeat = rows["invoice"].isin(rows.loc[repeated, "invoice"])

    is_cancel = rows["invoice"].str.startswith("C")
    is_product = rows["stock_code"].str.fullmatch(PRODUCT_CODE)
    zero_price = rows["price"] == 0
    no_customer = rows["customer_id"].isna()
    no_description = rows["description"].isna()
    written_off = (rows["quantity"] < 0) & ~is_cancel & zero_price
    given_away = (rows["quantity"] > 0) & zero_price
    plain_sale = (rows["quantity"] > 0) & ~zero_price & ~is_cancel & is_product
    raw_code = rows["stock_code_raw"]
    lowercase = raw_code.str.contains("[a-z]")

    recipes = [
        (in_overlap & has_repeat, 2, 16),
        (in_overlap & ~has_repeat, 3, SMALL_INVOICE),
        (~in_overlap & has_repeat, 2, 6),
        (is_cancel & is_product, 6, 3),
        (written_off & no_description, 2, 2),
        (written_off & ~no_description, 2, 2),
        (given_away & ~no_customer, 3, SMALL_INVOICE),
        (given_away & no_customer, 3, SMALL_INVOICE),
        (plain_sale & no_customer, 5, SMALL_INVOICE),
        (lowercase, 3, SMALL_INVOICE),
    ]
    recipes += [
        (rows["stock_code"] == code, 1, SMALL_INVOICE) for code in NON_PRODUCT_CODES
    ]

    picked = {POSITIVE_CANCELLATION, TRAILING_SPACE_INVOICE}
    for mask, count, cap in recipes:
        picked.update(pick_small(rows, lines, mask, count, cap))
    return picked


def pick_products(rows: pd.DataFrame) -> list[str]:
    """Return products with enough lines and enough returns for a daily table."""
    products = rows.loc[rows["stock_code"].str.fullmatch(PRODUCT_CODE)]
    per_code = products.groupby("stock_code").size()
    is_return = products["invoice"].str.startswith("C")
    returns = products.loc[is_return].groupby("stock_code").size()
    low, high = HISTORY_LINES
    fitting = per_code.loc[(per_code >= low) & (per_code <= high)].index
    with_returns = returns.loc[returns >= HISTORY_MIN_RETURNS].index
    return sorted(fitting.intersection(with_returns))[:N_HISTORY_PRODUCTS]


def parquet_sample(original: pd.DataFrame) -> pd.DataFrame:
    """Return the rows of the parquet fixture in file order, cache columns only."""
    rows = type_rows(original).assign(
        stock_code_raw=original["StockCode"].astype("str")
    )
    invoices = pick_invoices(rows)
    products = pick_products(rows)
    chosen = rows["invoice"].isin(invoices) | rows["stock_code"].isin(products)
    return rows.loc[chosen, [*NAMES, "sheet"]].reset_index(drop=True)


def xlsx_rows(sheet_rows: pd.DataFrame) -> pd.DataFrame:
    """Pick the rows of one sheet that go to the workbook, in file order.

    The first rows of the sheet, plus the first row of each kind that needs a
    cell type the reading task must handle.
    """
    is_text = sheet_rows["StockCode"].map(lambda cell: isinstance(cell, str))
    is_lower = sheet_rows["StockCode"].map(
        lambda cell: isinstance(cell, str) and cell != cell.upper()
    )
    has_space = sheet_rows["StockCode"].map(
        lambda cell: isinstance(cell, str) and cell != cell.strip()
    )
    invoice_text = sheet_rows["Invoice"].map(lambda cell: isinstance(cell, str))
    number_description = sheet_rows["Description"].map(
        lambda cell: isinstance(cell, int | float) and cell == cell
    )
    kinds = [
        invoice_text,
        is_text & ~invoice_text,
        is_lower,
        has_space,
        sheet_rows["Description"].isna(),
        sheet_rows["Customer ID"].isna(),
        number_description,
    ]
    position = set(range(XLSX_HEAD_ROWS))
    for kind in kinds:
        position.update(sheet_rows.index[kind][:1])
    return sheet_rows.loc[sorted(position), HEADERS].reset_index(drop=True)


def write_xlsx(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    """Write a workbook with fixed timestamps, so reruns give the same bytes."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=name, index=False)
    with zipfile.ZipFile(buffer) as source, zipfile.ZipFile(path, "w") as target:
        for info in source.infolist():
            content = source.read(info.filename)
            if info.filename == "docProps/core.xml":
                content = STAMPED_PROPERTY.sub(rb"\g<1>" + FIXED_STAMP, content)
            member = zipfile.ZipInfo(info.filename, date_time=FIXED_ZIP_TIME)
            member.compress_type = zipfile.ZIP_DEFLATED
            target.writestr(member, content)


def main() -> None:
    original = read_original()

    sample = parquet_sample(original)
    sample.to_parquet(PARQUET_OUT, index=False)
    print(f"{PARQUET_OUT}: {len(sample)} rows, {PARQUET_OUT.stat().st_size} bytes")

    workbook = {
        str(name): xlsx_rows(sheet_rows.reset_index(drop=True))
        for name, sheet_rows in original.groupby("sheet", sort=False)
    }
    write_xlsx(XLSX_OUT, workbook)
    total = sum(len(frame) for frame in workbook.values())
    print(f"{XLSX_OUT}: {total} rows, {XLSX_OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
