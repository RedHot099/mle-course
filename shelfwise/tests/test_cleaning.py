from shelfwise import cleaning


def test_keep_products_drops_postage(lines):
    kept = cleaning.keep_products(lines)
    assert "POST" not in set(kept["stock_code"])
    assert len(kept) == 5


def test_split_returns_marks_cancellations(lines):
    out = cleaning.split_returns(cleaning.keep_products(lines))
    assert out["qty_returned"].tolist() == [0, 4, 0, 0, 0]
    assert out["qty_sold"].tolist() == [10, 0, 6, 5, 0]


# >>> SOLUTION 17.1
def test_net_units_subtract_each_return_once(lines):
    out = cleaning.clean(lines)
    assert out.groupby("stock_code")["net_qty"].sum().to_dict() == {"21212": 11, "22333": 6}


def test_write_offs_are_not_negative_sales(lines):
    out = cleaning.clean(lines)
    write_off = out[(out["stock_code"] == "22333") & (out["quantity"] < 0)]
    assert write_off["net_qty"].tolist() == [0]


# --- STUB
# <<< SOLUTION
