<div align="center">

# Sales Insights with SQL and Python

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![pandas](https://img.shields.io/badge/pandas-CSV%20%2B%20SQL-orange)
![SQLite](https://img.shields.io/badge/SQLite-Analytics-green)
![matplotlib](https://img.shields.io/badge/matplotlib-Charts-red)
![Status](https://img.shields.io/badge/Status-Portfolio%20Project-purple)
[![CI](https://github.com/AmirhosseinHonardoust/Sales-Insights-SQL/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AmirhosseinHonardoust/Sales-Insights-SQL/actions/workflows/ci.yml)

</div>

A compact data-analytics project that turns raw retail transactions into **business KPIs**, using **SQL (SQLite)** for aggregation and **Python (pandas + matplotlib)** for visualization, with **automated tests**, **lint/type-check/coverage gates**, and **reproducible, checked-in-verified outputs**.

> **Important:** This project uses a **synthetic dataset** (10 products, 4 regions, one year of orders), not real transactional data.
>
> The pipeline, metrics, and charts are designed to demonstrate a professional, reproducible SQL-plus-Python analytics workflow. The revenue, AOV, and trend figures reflect the synthetic data only and should not be read as real business results.

---

## Table of Contents

- [Project Overview](#project-overview)
- [What This Project Does](#what-this-project-does)
- [What This Project Does Not Do](#what-this-project-does-not-do)
- [Key Features](#key-features)
- [System Workflow](#system-workflow)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Running the Pipeline](#running-the-pipeline)
- [Dataset](#dataset)
- [SQL Queries](#sql-queries)
- [Example Results](#example-results)
- [Visual Reports](#visual-reports)
- [Testing and CI](#testing-and-ci)
- [Code Quality](#code-quality)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Tech Stack](#tech-stack)
- [Author](#author)
- [License](#license)

---

## Project Overview

Sales dashboards are often shown as a finished product, without the workflow that produces them. This project shows that workflow end to end: raw CSV → SQLite table → SQL aggregation → CSV exports → charts, with every step covered by tests and a CI quality gate.

The goal is to demonstrate an honest, reproducible analytics pipeline, not just a set of pretty charts:

- move data from a flat file into a queryable SQL table
- express business KPIs as plain, readable SQL
- keep chart generation decoupled from query logic via a name-based label, not statement position
- verify the pipeline's own output, rather than trusting it silently

---

## What This Project Does

This project can:

- Load a retail sales CSV into a SQLite database
- Validate the CSV (required columns, no negative quantities/prices, parseable dates)
- Compute `revenue` automatically when it is missing from the source data
- Run five SQL analytics queries (revenue, top products, trend, AOV) from a single `queries.sql` file
- Export every query result to CSV
- Render a bar or line chart for the queries configured to have one
- Run automated tests and a linting/type-checking/coverage CI gate

---

## What This Project Does Not Do

This project does **not**:

- Connect to a live production database or warehouse
- Handle multi-currency, multi-tenant, or streaming data
- Provide a web dashboard or API, outputs are CSV/PNG files
- Forecast future sales or apply statistical modeling
- Validate business logic beyond basic column/type/range checks

A production analytics system would need a real data warehouse, scheduled ingestion, access control, and a BI/dashboard layer on top of this kind of pipeline.

---

## Key Features

- **SQLite-backed aggregation** | CSV rows loaded into a real SQL table, queried with plain SQL
- **Label-driven query dispatch** | each statement in `queries.sql` is tagged with a `-- name:` comment, so charts are matched by label, not by position, and the file can be reordered safely
- **CSV validation on load** | missing columns, negative quantities/prices, and unparseable dates raise clear, specific errors instead of failing silently
- **Chart generation decoupled from queries** | only labels present in a small config dict get a chart; everything else still gets its CSV
- **Editable-install packaging** | `pip install -e .` makes `create_db`, `analyze_sales`, and `utils` importable without path hacks
- **Full quality gate** | Ruff, Black, mypy, and pytest-cov enforced locally and in CI
- **Automated dependency updates** | Dependabot for pip and GitHub Actions

---

## System Workflow

```text
sales_data.csv
        ↓
CSV validation (columns, ranges, dates)
        ↓
SQLite table (create_db.py)
        ↓
Labeled SQL statements (queries.sql)
        ↓
Per-query CSV export
        ↓
Chart rendering for configured labels
        ↓
outputs/*.csv + outputs/charts/*.png
```

---

## Project Structure

```text
Sales-Insights-SQL/
│
├── .github/
│   ├── dependabot.yml
│   └── workflows/
│       └── ci.yml
│
├── data/
│   └── sales_data.csv
│
├── outputs/
│   ├── charts/
│   │   ├── revenue_by_region.png
│   │   └── monthly_sales_trend.png
│   ├── revenue_by_region.csv
│   ├── top_products_by_revenue.csv
│   ├── top_products_by_quantity.csv
│   ├── monthly_sales_trend.csv
│   └── aov_summary.csv
│
├── src/
│   ├── create_db.py
│   ├── queries.sql
│   ├── analyze_sales.py
│   └── utils.py
│
├── tests/
│   ├── conftest.py
│   ├── test_create_db.py
│   ├── test_analyze_sales.py
│   └── test_utils.py
│
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AmirhosseinHonardoust/Sales-Insights-SQL.git
cd Sales-Insights-SQL
```

### 2. Create a Virtual Environment

On Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

For development tools (Ruff, Black, mypy, pytest) and an editable install of the package itself:

```bash
pip install -r requirements-dev.txt
```

---

## Quick Start

Build the SQLite database:

```bash
python src/create_db.py --csv data/sales_data.csv --db sales.db
```

Run the SQL analytics and generate charts:

```bash
python src/analyze_sales.py --db sales.db --sql src/queries.sql --outdir outputs
```

---

## Running the Pipeline

`create_db.py` reads the CSV, validates it, computes `revenue` if missing, and loads it into a SQLite table. `analyze_sales.py` then runs every labeled statement in `queries.sql` against that table, writes a CSV per label, and renders a chart for any label configured in `CHART_CONFIG`.

```bash
python src/create_db.py --csv data/sales_data.csv --db sales.db
python src/analyze_sales.py --db sales.db --sql src/queries.sql --outdir outputs
```

Generated outputs include:

```text
outputs/revenue_by_region.csv
outputs/top_products_by_revenue.csv
outputs/top_products_by_quantity.csv
outputs/monthly_sales_trend.csv
outputs/aov_summary.csv
outputs/charts/revenue_by_region.png
outputs/charts/monthly_sales_trend.png
```

---

## Dataset

A **synthetic dataset** of 10 products sold across 4 regions (North, South, East, West) over one year.

<div align="center">

| Column | Description |
|---|---|
| `order_id` | Unique order identifier |
| `date` | Order date (`YYYY-MM-DD`) |
| `region` | Sales region |
| `product` | Product name |
| `quantity` | Quantity sold |
| `unit_price` | Unit price of the product |
| `revenue` | Calculated as `quantity × unit_price` if not already present |

</div>

Example preview:

<div align="center">

| order_id | date | region | product | quantity | unit_price | revenue |
|---|---|---|---|---|---|---|
| 1000 | 2024-01-01 | South | Laptop | 1 | 1170.68 | 1170.68 |
| 1000 | 2024-01-01 | South | Mouse | 3 | 25.41 | 76.23 |
| 1001 | 2024-01-01 | South | Mouse | 4 | 24.59 | 98.36 |

</div>

---

## SQL Queries

Inside `src/queries.sql`, five core analyses are defined, each preceded by a `-- name: <label>` comment that `analyze_sales.py` uses to name outputs and pick charts:

<div align="center">

| Query | Label | Description |
|---|---|---|
| Revenue by Region | `revenue_by_region` | Total revenue per region |
| Top Products by Revenue | `top_products_by_revenue` | Best-selling products by revenue |
| Top Products by Quantity | `top_products_by_quantity` | Most purchased products by quantity |
| Monthly Sales Trend | `monthly_sales_trend` | Revenue trend over time |
| Average Order Value | `aov_summary` | Revenue per order by region |

</div>

Example statement:

```sql
-- name: revenue_by_region
SELECT region, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;
```

---

## Example Results

Example numbers from the included run against `data/sales_data.csv`:

<div align="center">

| Region | Total Revenue | Orders | AOV |
|---|---|---|---|
| West | $3,863,611.34 | 2,272 | $1,700.53 |
| North | $3,808,908.00 | 2,324 | $1,638.94 |
| East | $3,595,279.81 | 2,195 | $1,637.94 |
| South | $3,454,678.67 | 2,188 | $1,578.92 |

</div>

<div align="center">

| Product | Total Revenue |
|---|---|
| Laptop | $4,929,052.61 |
| Smartphone | $3,597,663.09 |
| Tablet | $2,242,695.88 |
| Monitor | $997,930.52 |
| Desk | $921,657.40 |

</div>

> West leads total revenue, though all four regions are within about 12% of each other. Laptops and Smartphones dominate product revenue, together accounting for about 58% of total sales (~$14.7M). Higher AOV in the West suggests more premium or bulk purchases there, though the regional gap is modest (~7% top to bottom).

---

## Visual Reports

### Revenue and trend charts

<div align="center">

| Revenue by Region | Monthly Sales Trend |
|---|---|
| ![Revenue by region](https://github.com/user-attachments/assets/6b9ba0bc-1299-416d-8de4-6e49d2ed7968) | ![Monthly sales trend](https://github.com/user-attachments/assets/b5a403a4-6ae2-4f1d-998c-5073ff7bb676) |
| **Analysis:** West leads total revenue, but all four regions sit within about 12% of each other, so regional performance is fairly even in this dataset. | **Analysis:** Monthly revenue is fairly stable (~$1.08M–$1.35M) with no strong seasonal ramp, February is the low point and March the peak, and the synthetic data doesn't show a consistent Q3/Q4 rise. |

</div>

---

## Testing and CI

Run unit tests locally:

```bash
pytest --cov --cov-report=term-missing
```

Compile source files, lint, format-check, and type-check:

```bash
ruff check .
black --check .
mypy
```

The GitHub Actions workflow checks:

- dependency installation (with pip caching)
- linting with Ruff
- formatting with Black
- type-checking with mypy
- unit tests with coverage (`pytest --cov`, gate enforced at 95%)

CI is defined in:

```text
.github/workflows/ci.yml
```

Dependency updates (pip and GitHub Actions) are proposed automatically via `.github/dependabot.yml`.

---

## Code Quality

The project separates responsibilities across modules:

<div align="center">

| Module | Purpose |
|---|---|
| `src/create_db.py` | Loads and validates the CSV, computes `revenue` if missing, writes the SQLite table |
| `src/queries.sql` | Labeled SQL statements for every business metric |
| `src/analyze_sales.py` | Runs labeled queries, exports CSVs, dispatches charts by label |
| `src/utils.py` | Shared I/O and plotting helpers (`save_csv`, `plot_bar`, `plot_line`) |

</div>

Tooling is configured through `pyproject.toml` (Ruff, Black, mypy, pytest, coverage) and `requirements-dev.txt`. See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup and the full gate.

---

## Limitations

This project has important limitations:

- The dataset is synthetic and small, not a production sales corpus
- There is no live database connection, everything runs against a local SQLite file
- `queries.sql` is split on `;`, which would break on a query containing a semicolon inside a string literal
- Dependencies are pinned to exact versions with no lockfile-based range strategy beyond Dependabot's weekly PRs
- There is no dashboard or API, results are CSV/PNG files on disk

The project is strongest as a portfolio demonstration of a clean, tested SQL-plus-Python analytics workflow.

---

## Future Improvements

Potential next improvements:

- Add a real (or realistic) multi-year dataset with seasonality
- Add a lightweight dashboard (e.g. Streamlit) on top of the existing outputs
- Support additional database backends (PostgreSQL, DuckDB)
- Add data-quality checks beyond column/range/date validation (e.g. duplicate order detection)
- Add an integration test that runs the CLIs end to end as subprocesses

---

## Tech Stack

- Python
- pandas
- SQLite
- matplotlib
- pytest
- Ruff
- Black
- mypy
- GitHub Actions

---

## Author

**Amir Honardoust**

GitHub: [@AmirhosseinHonardoust](https://github.com/AmirhosseinHonardoust)

---

## License

This project is licensed under the [MIT License](LICENSE).
