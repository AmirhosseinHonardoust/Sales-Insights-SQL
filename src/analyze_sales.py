#!/usr/bin/env python3
from __future__ import annotations
import argparse
import sqlite3
from pathlib import Path
import pandas as pd
from utils import ensure_outdir, save_csv, plot_bar, plot_line

def run_queries(db_path: str | Path, sql_file: str | Path, outdir: str | Path) -> None:
    outdir = ensure_outdir(outdir)
    charts = ensure_outdir(Path(outdir) / 'charts')
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_text = f.read()
    statements = [s.strip() for s in sql_text.split(';') if s.strip()]
    labels = [
        ('revenue_by_region', 'region', 'total_revenue'),
        ('top_products_by_revenue', 'product', 'total_revenue'),
        ('top_products_by_quantity', 'product', 'total_qty'),
        ('monthly_sales_trend', 'month', 'total_revenue'),
        ('aov_summary', 'region', 'aov'),
    ]

    with sqlite3.connect(db_path) as con:
        for i, stmt in enumerate(statements):
            label = labels[i][0] if i < len(labels) else f'result_{i+1}'
            df = pd.read_sql_query(stmt, con)
            save_csv(df, Path(outdir) / f'{label}.csv')
            if label == 'revenue_by_region' and not df.empty:
                plot_bar(df, 'region', 'total_revenue', 'Revenue by Region', charts / 'revenue_by_region.png')
            if label == 'monthly_sales_trend' and not df.empty:
                plot_line(df, 'month', 'total_revenue', 'Monthly Sales Trend', charts / 'monthly_sales_trend.png')

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description='Run SQL analytics and export results')
    ap.add_argument('--db', default='sales.db', help='path to SQLite DB')
    ap.add_argument('--sql', default='src/queries.sql', help='path to queries.sql')
    ap.add_argument('--outdir', default='outputs', help='output directory')
    return ap.parse_args()

def main() -> None:
    args = parse_args()
    run_queries(args.db, args.sql, args.outdir)
    print(f'Artifacts saved to: {Path(args.outdir).resolve()}')

if __name__ == '__main__':
    main()
