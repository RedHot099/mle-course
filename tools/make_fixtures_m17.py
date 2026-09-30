"""Build the invoice-lines sample that the module 17 checks run on.

Author-only tool, run after module 06's cache exists:

    uv run python tools/make_fixtures_m17.py

The products are chosen so that every planted defect of shelfwise shows:
cancellations, write-offs, several descriptions per code, Sunday sales and
a product whose last sale is older than the price look-back.
"""

import pandas as pd

from coursekit import paths

CACHE = paths.ONLINE_RETAIL.with_suffix(".parquet")
OUT = paths.FIXTURES_DIR / "shelfwise_lines.parquet"
PER_KIND = 2


def main() -> None:
    lines = pd.read_parquet(CACHE)
    lines = lines.assign(code=lines["stock_code"].str.strip().str.upper())
    lines = lines[lines["code"].str.match(r"^\d{5}[A-Z]{0,2}$")]
    lines = lines.assign(
        week=lines["invoice_date"].dt.normalize()
        - pd.to_timedelta(lines["invoice_date"].dt.weekday, unit="D")
    )
    by_code = lines.groupby("code").agg(
        weeks=("week", "nunique"),
        last=("invoice_date", "max"),
        cancels=("invoice", lambda s: s.str.startswith("C").sum()),
        writeoffs=(
            "quantity",
            lambda q: (
                (q < 0) & ~lines.loc[q.index, "invoice"].str.startswith("C")
            ).sum(),
        ),
        descriptions=("description", "nunique"),
        sundays=("invoice_date", lambda d: (d.dt.weekday == 6).sum()),
    )
    active = by_code[by_code["weeks"] >= 30]
    end = lines["invoice_date"].max()
    chosen: list[str] = []
    for column in ("cancels", "writeoffs", "descriptions", "sundays"):
        ranked = active.drop(index=chosen).sort_values(
            [column, "weeks"], ascending=False
        )
        chosen += list(ranked.index[:PER_KIND])
    stale = active[active["last"] < end - pd.Timedelta(weeks=20)].drop(
        index=chosen, errors="ignore"
    )
    chosen += list(stale.sort_values("weeks", ascending=False).index[:1])

    sample = lines[lines["code"].isin(chosen)].drop(columns=["code", "week"])
    sample = sample.sort_values(["invoice_date", "invoice"]).reset_index(drop=True)
    sample.to_parquet(OUT, index=False, compression="zstd", compression_level=19)
    print(
        f"{OUT.name}: {len(sample)} lines, {len(chosen)} products, "
        f"{OUT.stat().st_size} bytes"
    )
    print(active.loc[chosen].to_string())


if __name__ == "__main__":
    main()
