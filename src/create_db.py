#!/usr/bin/env python3
from __future__ import annotations
import argparse
import sqlite3
from pathlib import Path
import pandas as pd

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

def load_csv_to_db(csv_path: str | Path, db_path: str | Path) -> None:
    csv_path = Path(csv_path)
    db_path = Path(db_path)
    df = pd.read_csv(csv_path, parse_dates=['date'])
    if 'revenue' not in df.columns:
        df['revenue'] = df['quantity'] * df['unit_price']
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    with sqlite3.connect(db_path) as con:
        con.execute(SCHEMA)
        df.to_sql('sales', con, if_exists='replace', index=False)

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description='Create SQLite DB from sales CSV')
    ap.add_argument('--csv', required=True, help='path to sales_data.csv')
    ap.add_argument('--db', default='sales.db', help='output SQLite DB path')
    return ap.parse_args()

def main() -> None:
    args = parse_args()
    load_csv_to_db(args.csv, args.db)
    print(f'Loaded {args.csv} → {args.db} (table: sales)')

if __name__ == '__main__':
    main()
