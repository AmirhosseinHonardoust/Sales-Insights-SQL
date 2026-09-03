#!/usr/bin/env python3
"""Load a sales CSV into a SQLite database.

Usage:
    python src/create_db.py --csv data/sales_data.csv --db sales.db
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS sales (
    order_id      INTEGER,
    date          TEXT,
    region        TEXT,
    product       TEXT,
    quantity      INTEGER,
    unit_price    REAL,
    revenue       REAL
);
"""

REQUIRED_COLUMNS = {"order_id", "date", "region", "product", "quantity", "unit_price"}


def load_csv_to_db(csv_path: str | Path, db_path: str | Path) -> None:
    """Read ``csv_path``, compute revenue if missing, and load it into ``db_path``.

    Raises:
        FileNotFoundError: if ``csv_path`` does not exist.
        ValueError: if the CSV is missing any required column.
    """
    csv_path = Path(csv_path)
    db_path = Path(db_path)

    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV {csv_path} is missing required column(s): {sorted(missing)}")

    for col in ("quantity", "unit_price"):
        if (df[col] < 0).any():
            bad_rows = df.index[df[col] < 0].tolist()
            raise ValueError(f"CSV {csv_path} has negative '{col}' values at row(s): {bad_rows}")

    if "revenue" not in df.columns:
        df["revenue"] = df["quantity"] * df["unit_price"]

    # Parse explicitly (rather than via read_csv's parse_dates) so a bad value
    # is reported as a clear ValueError instead of silently leaving the column
    # as text, which used to crash later with a confusing AttributeError on
    # the .dt accessor.
    parsed_dates = pd.to_datetime(df["date"], errors="coerce")
    if parsed_dates.isna().any():
        bad_rows = df.index[parsed_dates.isna()].tolist()
        raise ValueError(f"CSV {csv_path} has unparseable 'date' values at row(s): {bad_rows}")
    df["date"] = parsed_dates.dt.strftime("%Y-%m-%d")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        con.execute(SCHEMA)
        df.to_sql("sales", con, if_exists="replace", index=False)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Create SQLite DB from sales CSV")
    ap.add_argument("--csv", required=True, help="path to sales_data.csv")
    ap.add_argument("--db", default="sales.db", help="output SQLite DB path")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    load_csv_to_db(args.csv, args.db)
    logger.info("Loaded %s → %s (table: sales)", args.csv, args.db)


if __name__ == "__main__":  # pragma: no cover
    main()
