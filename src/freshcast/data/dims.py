"""Dimension tables: one row per store or product, joined back to the facts."""

import pandas as pd

from freshcast.data.schema import CITY, HIERARCHY, TARGET


def build_store_dim(df: pd.DataFrame) -> pd.DataFrame:
    """Build the store dimension: one row per store.

    Args:
        df: Daily sales with ``store_id``, ``city_id``, ``product_id`` and
            the target.

    Returns:
        A frame with ``store_id``, ``city_id``, ``n_products`` (distinct
        products sold in the store) and ``mean_sales`` (mean daily sales per
        series row), sorted by ``store_id``.

    Raises:
        ValueError: A store appears in more than one city.
    """
    # >>> SOLUTION 07.3
    cities_per_store = df.groupby("store_id")[CITY].nunique()
    ambiguous = int((cities_per_store > 1).sum())
    if ambiguous:
        raise ValueError(f"{ambiguous} stores appear in more than one city.")

    return (
        df.groupby("store_id", as_index=False)
        .agg(
            city_id=(CITY, "first"),
            n_products=("product_id", "nunique"),
            mean_sales=(TARGET, "mean"),
        )
        .sort_values("store_id")
        .reset_index(drop=True)
    )
    # <<< SOLUTION


def build_product_dim(df: pd.DataFrame) -> pd.DataFrame:
    """Build the product dimension: one row per product.

    Args:
        df: Rows with ``product_id``, ``store_id`` and the four hierarchy
            columns.

    Returns:
        A frame with ``product_id``, the four hierarchy columns and
        ``n_stores`` (distinct stores selling the product), sorted by
        ``product_id``.

    Raises:
        ValueError: A product appears under more than one hierarchy path.
    """
    # >>> SOLUTION 07.3
    paths = df[["product_id", *HIERARCHY]].drop_duplicates()
    ambiguous = int(paths["product_id"].duplicated().sum())
    if ambiguous:
        raise ValueError(f"{ambiguous} products have more than one hierarchy path.")

    n_stores = df.groupby("product_id", as_index=False).agg(
        n_stores=("store_id", "nunique")
    )
    return (
        paths.merge(n_stores, on="product_id", how="left", validate="one_to_one")
        .sort_values("product_id")
        .reset_index(drop=True)
    )
    # <<< SOLUTION


def attach_dim(fact: pd.DataFrame, dim: pd.DataFrame, on: str) -> pd.DataFrame:
    """Add the columns of a dimension to a fact table.

    The join can neither add nor drop fact rows: a key repeated in ``dim``
    or a fact key missing from ``dim`` is an error, not something to work
    around later.

    Args:
        fact: The table to extend, many rows per key.
        dim: The dimension, exactly one row per key.
        on: Name of the key column, present in both.

    Returns:
        ``fact`` with the dimension's other columns appended, rows in the
        original order.

    Raises:
        pandas.errors.MergeError: ``dim`` has a repeated key.
        ValueError: Some fact rows have a key that ``dim`` lacks.
    """
    # >>> SOLUTION 07.3
    merged = fact.merge(dim, on=on, how="left", validate="many_to_one", indicator=True)
    unmatched = int((merged["_merge"] != "both").sum())
    if unmatched:
        raise ValueError(
            f"{unmatched} fact rows have a {on} absent from the dimension."
        )
    return merged.drop(columns="_merge")
    # <<< SOLUTION
