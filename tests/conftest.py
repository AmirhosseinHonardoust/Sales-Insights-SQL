from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd
import pytest

matplotlib.use("Agg")  # headless-safe backend for tests

# create_db / analyze_sales / utils are importable as top-level modules because
# the project is installed in editable mode (see `-e .` in requirements-dev.txt
# and the [tool.setuptools] package-dir mapping in pyproject.toml) rather than
# via a sys.path hack.

# Small, hand-checkable dataset:
# - order 1 has two line items in North (tests COUNT(DISTINCT order_id))
# - two regions, two products, two months -> easy to verify aggregates by hand
SAMPLE_ROWS = [
    # order_id, date,       region, product, quantity, unit_price
    (1, "2024-01-01", "North", "Widget", 2, 10.0),
    (1, "2024-01-01", "North", "Gadget", 1, 5.0),
    (2, "2024-01-15", "South", "Widget", 1, 10.0),
    (3, "2024-02-01", "North", "Gadget", 3, 5.0),
    (4, "2024-02-10", "South", "Widget", 2, 10.0),
]
COLUMNS = ["order_id", "date", "region", "product", "quantity", "unit_price"]


@pytest.fixture
def sample_df() -> pd.DataFrame:
    df = pd.DataFrame(SAMPLE_ROWS, columns=COLUMNS)
    df["revenue"] = df["quantity"] * df["unit_price"]
    return df


@pytest.fixture
def sample_csv(tmp_path: Path, sample_df: pd.DataFrame) -> Path:
    path = tmp_path / "sample_sales.csv"
    # write WITHOUT the revenue column so create_db's compute-if-missing path is exercised
    sample_df.drop(columns=["revenue"]).to_csv(path, index=False)
    return path
