from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from analyze_sales import parse_statements, run_queries
from create_db import load_csv_to_db

QUERIES_SQL = """
-- name: revenue_by_region
SELECT region, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;

-- name: monthly_sales_trend
SELECT strftime('%Y-%m', date) AS month, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY month
ORDER BY month ASC;
"""

# Same two statements, reordered, to prove labels no longer depend on position.
QUERIES_SQL_REORDERED = """
-- name: monthly_sales_trend
SELECT strftime('%Y-%m', date) AS month, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY month
ORDER BY month ASC;

-- name: revenue_by_region
SELECT region, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;
"""


def test_parse_statements_extracts_labels() -> None:
    parsed = parse_statements(QUERIES_SQL)
    labels = [label for label, _ in parsed]
    assert labels == ["revenue_by_region", "monthly_sales_trend"]
    assert all("SELECT" in stmt for _, stmt in parsed)


def test_parse_statements_falls_back_when_unlabeled() -> None:
    parsed = parse_statements("SELECT 1;\nSELECT 2;")
    assert [label for label, _ in parsed] == ["result_1", "result_2"]


@pytest.fixture
def db_path(sample_csv: Path, tmp_path: Path) -> Path:
    db = tmp_path / "sales.db"
    load_csv_to_db(sample_csv, db)
    return db


def test_run_queries_produces_correct_aggregates(db_path: Path, tmp_path: Path) -> None:
    sql_file = tmp_path / "queries.sql"
    sql_file.write_text(QUERIES_SQL)
    outdir = tmp_path / "outputs"

    run_queries(db_path, sql_file, outdir)

    by_region = pd.read_csv(outdir / "revenue_by_region.csv").set_index("region")["total_revenue"]
    # North: (2*10 + 1*5) + (3*5) = 25 + 15 = 40.0; South: (1*10) + (2*10) = 30.0
    assert by_region["North"] == 40.0
    assert by_region["South"] == 30.0

    assert (outdir / "charts" / "revenue_by_region.png").is_file()
    assert (outdir / "charts" / "monthly_sales_trend.png").is_file()


def test_run_queries_labels_by_name_not_position(db_path: Path, tmp_path: Path) -> None:
    """Regression test: reordering statements must not swap which chart/CSV
    a result lands in (the original script matched by list index)."""
    sql_file = tmp_path / "queries.sql"
    sql_file.write_text(QUERIES_SQL_REORDERED)
    outdir = tmp_path / "outputs"

    run_queries(db_path, sql_file, outdir)

    by_region = pd.read_csv(outdir / "revenue_by_region.csv")
    assert set(by_region.columns) == {"region", "total_revenue"}

    trend = pd.read_csv(outdir / "monthly_sales_trend.csv")
    assert set(trend.columns) == {"month", "total_revenue"}


def test_run_queries_missing_db_raises(tmp_path: Path) -> None:
    sql_file = tmp_path / "queries.sql"
    sql_file.write_text(QUERIES_SQL)
    with pytest.raises(FileNotFoundError):
        run_queries(tmp_path / "no.db", sql_file, tmp_path / "outputs")


def test_monthly_trend_chart_uses_date_axis_not_categorical(
    db_path: Path, tmp_path: Path, recwarn: pytest.WarningsRecorder
) -> None:
    """Regression test: the x-axis for monthly_sales_trend must be parsed as
    dates before plotting, or matplotlib emits a 'categorical units' warning
    and treats month labels as arbitrary, unordered categories."""
    sql_file = tmp_path / "queries.sql"
    sql_file.write_text(QUERIES_SQL)

    run_queries(db_path, sql_file, tmp_path / "outputs")

    categorical_warnings = [
        w for w in recwarn.list if "categorical units" in str(w.message).lower()
    ]
    assert not categorical_warnings
