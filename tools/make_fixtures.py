"""Build the small FreshRetailNet sample that task checks run on.

Author-only tool. Run from the repository root after `course data`:

    uv run python tools/make_fixtures.py

The sample keeps the raw schema and all 90 days of a few series chosen so
that every anomaly the checks rely on is present.
"""

import pandas as pd

from coursekit import paths

# (store_id, product_id) pairs. City 3: two stores, including series with the
# `discount == 0` placeholder. City 11: product 37 has discounts above 1.
_N_PLACEHOLDER_SERIES = 2
_N_PLAIN_SERIES = 4
_ABOVE_ONE_STORE = 293
_ABOVE_ONE_PRODUCT = 37


def main() -> None:
    raw = pd.read_parquet(paths.FRN_TRAIN, filters=[("city_id", "in", [3, 11])])
    city3 = raw[raw["city_id"] == 3]

    placeholder_keys = (
        city3.loc[city3["discount"] == 0, ["store_id", "product_id"]]
        .drop_duplicates()
        .sort_values(["store_id", "product_id"])
        .head(_N_PLACEHOLDER_SERIES)
    )
    stores = placeholder_keys["store_id"].unique()
    plain_keys = (
        city3.loc[city3["store_id"].isin(stores), ["store_id", "product_id"]]
        .drop_duplicates()
        .merge(placeholder_keys, how="left", indicator=True)
        .query("_merge == 'left_only'")
        .drop(columns="_merge")
        .sort_values(["store_id", "product_id"])
        .head(_N_PLAIN_SERIES)
    )
    store11 = raw[raw["store_id"] == _ABOVE_ONE_STORE]
    other_product = int(
        store11.loc[store11["product_id"] != _ABOVE_ONE_PRODUCT, "product_id"].min()
    )
    city11_keys = pd.DataFrame(
        {
            "store_id": [_ABOVE_ONE_STORE, _ABOVE_ONE_STORE],
            "product_id": [_ABOVE_ONE_PRODUCT, other_product],
        }
    )

    keys = pd.concat([placeholder_keys, plain_keys, city11_keys], ignore_index=True)
    sample = raw.merge(keys, on=["store_id", "product_id"], validate="many_to_one")
    # Shuffle so the file is unsorted, like the original.
    sample = sample.sample(frac=1.0, random_state=7).reset_index(drop=True)

    out = paths.FIXTURES_DIR / "frn_sample.parquet"
    sample.to_parquet(out, index=False)
    print(f"{out}: {len(sample)} rows, {len(keys)} series, {out.stat().st_size} bytes")
    print(f"  discount == 0: {(sample['discount'] == 0).sum()} rows")
    print(f"  discount > 1:  {(sample['discount'] > 1).sum()} rows")


if __name__ == "__main__":
    main()
