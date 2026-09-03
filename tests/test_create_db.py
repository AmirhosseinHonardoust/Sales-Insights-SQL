from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from create_db import load_csv_to_db, main, parse_args


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


@pytest.mark.parametrize("bad_col", ["quantity", "unit_price"])
def test_load_csv_to_db_negative_values_raise(tmp_path: Path, bad_col: str) -> None:
    row = {
        "order_id": [1],
        "date": ["2024-01-01"],
        "region": ["North"],
        "product": ["Widget"],
        "quantity": [2],
        "unit_price": [10.0],
    }
    row[bad_col] = [-1]
    bad_csv = tmp_path / "negative.csv"
    pd.DataFrame(row).to_csv(bad_csv, index=False)
    with pytest.raises(ValueError, match=f"negative '{bad_col}'"):
        load_csv_to_db(bad_csv, tmp_path / "sales.db")


def test_load_csv_to_db_unparseable_date_raises(tmp_path: Path) -> None:
    """Regression test: a bad date value must raise a clear ValueError instead
    of crashing later with 'Can only use .dt accessor with datetimelike values'."""
    bad_csv = tmp_path / "bad_date.csv"
    pd.DataFrame(
        {
            "order_id": [1],
            "date": ["not-a-date"],
            "region": ["North"],
            "product": ["Widget"],
            "quantity": [2],
            "unit_price": [10.0],
        }
    ).to_csv(bad_csv, index=False)
    with pytest.raises(ValueError, match="unparseable 'date'"):
        load_csv_to_db(bad_csv, tmp_path / "sales.db")


def test_parse_args_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["create_db.py", "--csv", "data/sales_data.csv"])
    args = parse_args()
    assert args.csv == "data/sales_data.csv"
    assert args.db == "sales.db"


def test_main_loads_csv_to_db(
    monkeypatch: pytest.MonkeyPatch, sample_csv: Path, tmp_path: Path
) -> None:
    db_path = tmp_path / "sales.db"
    monkeypatch.setattr(
        "sys.argv", ["create_db.py", "--csv", str(sample_csv), "--db", str(db_path)]
    )
    main()
    assert db_path.is_file()
    with sqlite3.connect(db_path) as con:
        count = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    assert count == 5
