from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import pytest

from analyze_sales import main, parse_args, parse_statements, run_queries
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


def test_run_queries_missing_sql_file_raises(db_path: Path, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="SQL file not found"):
        run_queries(db_path, tmp_path / "no.sql", tmp_path / "outputs")


def test_run_queries_no_statements_raises(db_path: Path, tmp_path: Path) -> None:
    sql_file = tmp_path / "empty.sql"
    sql_file.write_text("   \n  ;  \n")
    with pytest.raises(ValueError, match="No SQL statements found"):
        run_queries(db_path, sql_file, tmp_path / "outputs")


def test_run_queries_skips_chart_for_label_not_in_config(db_path: Path, tmp_path: Path) -> None:
    """A labeled query outside CHART_CONFIG (e.g. top_products_by_revenue) gets
    a CSV but no chart, and an empty result set is skipped too."""
    sql_file = tmp_path / "queries.sql"
    sql_file.write_text("""
-- name: top_products_by_revenue
SELECT product, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales GROUP BY product ORDER BY total_revenue DESC;

-- name: no_rows
SELECT product, revenue FROM sales WHERE 1 = 0;
""")
    outdir = tmp_path / "outputs"

    run_queries(db_path, sql_file, outdir)

    assert (outdir / "top_products_by_revenue.csv").is_file()
    assert not (outdir / "charts" / "top_products_by_revenue.png").exists()
    assert (outdir / "no_rows.csv").is_file()
    assert not (outdir / "charts" / "no_rows.png").exists()


def test_run_queries_warns_and_skips_chart_on_column_mismatch(
    db_path: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """A labeled query in CHART_CONFIG whose result is missing the expected
    x/y columns logs a warning and skips the chart instead of crashing."""
    sql_file = tmp_path / "queries.sql"
    sql_file.write_text("""
-- name: revenue_by_region
SELECT region AS not_region, revenue AS not_total_revenue FROM sales LIMIT 1;
""")
    outdir = tmp_path / "outputs"

    with caplog.at_level(logging.WARNING):
        run_queries(db_path, sql_file, outdir)

    assert "Skipping chart for revenue_by_region" in caplog.text
    assert not (outdir / "charts" / "revenue_by_region.png").exists()


def test_parse_args_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["analyze_sales.py"])
    args = parse_args()
    assert args.db == "sales.db"
    assert args.sql == "src/queries.sql"
    assert args.outdir == "outputs"


def test_main_runs_queries(monkeypatch: pytest.MonkeyPatch, db_path: Path, tmp_path: Path) -> None:
    sql_file = tmp_path / "queries.sql"
    sql_file.write_text(QUERIES_SQL)
    outdir = tmp_path / "outputs"
    monkeypatch.setattr(
        "sys.argv",
        ["analyze_sales.py", "--db", str(db_path), "--sql", str(sql_file), "--outdir", str(outdir)],
    )
    main()
    assert (outdir / "revenue_by_region.csv").is_file()


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
