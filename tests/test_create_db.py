from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from create_db import load_csv_to_db


def test_load_csv_to_db_computes_revenue_when_missing(sample_csv: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "sales.db"
    load_csv_to_db(sample_csv, db_path)

    with sqlite3.connect(db_path) as con:
        df = pd.read_sql_query("SELECT * FROM sales ORDER BY order_id, product", con)

    assert len(df) == 5
    assert set(df.columns) == {
        "order_id",
        "date",
        "region",
        "product",
        "quantity",
        "unit_price",
        "revenue",
    }
    # revenue = quantity * unit_price for every row
    assert (df["revenue"] == df["quantity"] * df["unit_price"]).all()
    # dates normalized to YYYY-MM-DD strings
    assert set(df["date"]) == {"2024-01-01", "2024-01-15", "2024-02-01", "2024-02-10"}


def test_load_csv_to_db_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_csv_to_db(tmp_path / "does_not_exist.csv", tmp_path / "sales.db")


def test_load_csv_to_db_missing_column_raises(tmp_path: Path) -> None:
    bad_csv = tmp_path / "bad.csv"
    pd.DataFrame({"order_id": [1], "date": ["2024-01-01"]}).to_csv(bad_csv, index=False)
    with pytest.raises(ValueError, match="missing required column"):
        load_csv_to_db(bad_csv, tmp_path / "sales.db")
