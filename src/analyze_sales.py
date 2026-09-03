#!/usr/bin/env python3
"""Run the SQL analytics in queries.sql against a sales SQLite DB and export
each result to CSV, plus a couple of charts for the headline metrics.

Usage:
    python src/analyze_sales.py --db sales.db --sql src/queries.sql --outdir outputs
"""

from __future__ import annotations

import argparse
import logging
import re
import sqlite3
from pathlib import Path

import pandas as pd

from utils import ensure_outdir, plot_bar, plot_line, save_csv

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

_NAME_RE = re.compile(r"^\s*--\s*name:\s*(\S+)\s*$", re.IGNORECASE)

# Which output labels get a chart, and how to draw it. Keyed by the "-- name:"
# label in queries.sql, NOT by statement position, so queries.sql can be
# reordered or extended without silently mismatching charts to results.
CHART_CONFIG: dict[str, tuple[str, str, str, str]] = {
    # label: (chart_kind, x_column, y_column, title)
    "revenue_by_region": ("bar", "region", "total_revenue", "Revenue by Region"),
    "monthly_sales_trend": ("line", "month", "total_revenue", "Monthly Sales Trend"),
}


def parse_statements(sql_text: str) -> list[tuple[str, str]]:
    """Split ``sql_text`` into (label, statement) pairs.

    Each statement should be preceded by a ``-- name: <label>`` comment line;
    statements without one fall back to ``result_<n>`` (1-indexed) so the
    file still works if a label is forgotten.
    """
    blocks = [b for b in sql_text.split(";") if b.strip()]
    parsed: list[tuple[str, str]] = []
    for i, block in enumerate(blocks, start=1):
        label = f"result_{i}"
        kept_lines = []
        for line in block.splitlines():
            match = _NAME_RE.match(line)
            if match:
                label = match.group(1)
                continue
            kept_lines.append(line)
        statement = "\n".join(kept_lines).strip()
        if statement:
            parsed.append((label, statement))
    return parsed


def run_queries(db_path: str | Path, sql_file: str | Path, outdir: str | Path) -> None:
    """Execute every statement in ``sql_file`` against ``db_path``, saving each
    result as a CSV in ``outdir`` (and a chart for any label in CHART_CONFIG)."""
    db_path = Path(db_path)
    sql_file = Path(sql_file)

    if not db_path.is_file():
        raise FileNotFoundError(f"Database not found: {db_path}. Run create_db.py first.")
    if not sql_file.is_file():
        raise FileNotFoundError(f"SQL file not found: {sql_file}")

    outdir = ensure_outdir(outdir)
    charts = ensure_outdir(Path(outdir) / "charts")

    sql_text = sql_file.read_text(encoding="utf-8")
    statements = parse_statements(sql_text)
    if not statements:
        raise ValueError(f"No SQL statements found in {sql_file}")

    with sqlite3.connect(db_path) as con:
        for label, stmt in statements:
            df = pd.read_sql_query(stmt, con)
            save_csv(df, Path(outdir) / f"{label}.csv")
            logger.info("Saved %s.csv (%d rows)", label, len(df))

            if label not in CHART_CONFIG or df.empty:
                continue
            kind, x, y, title = CHART_CONFIG[label]
            if x not in df.columns or y not in df.columns:
                logger.warning(
                    "Skipping chart for %s: expected columns %r/%r not in result %r",
                    label,
                    x,
                    y,
                    list(df.columns),
                )
                continue
            plot_fn = plot_bar if kind == "bar" else plot_line
            plot_fn(df, x, y, title, charts / f"{label}.png")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run SQL analytics and export results")
    ap.add_argument("--db", default="sales.db", help="path to SQLite DB")
    ap.add_argument("--sql", default="src/queries.sql", help="path to queries.sql")
    ap.add_argument("--outdir", default="outputs", help="output directory")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    run_queries(args.db, args.sql, args.outdir)
    logger.info("Artifacts saved to: %s", Path(args.outdir).resolve())


if __name__ == "__main__":
    main()
