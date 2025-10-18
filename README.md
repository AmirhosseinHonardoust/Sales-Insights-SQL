# Sales Insights with SQL and Python

Analyze a retail sales dataset using **SQL (SQLite)** for data aggregation and **Python** for visualization.  
This project demonstrates how to move from raw transactional data → structured SQL database → actionable business insights with clear visuals.

---

## Project Overview

This project combines **data engineering**, **SQL analytics**, and **data visualization** to uncover key sales insights from a retail dataset.  
You’ll see how SQL handles powerful data aggregation, while Python brings the results to life with visualizations.

**Workflow:**
1. Load CSV data → SQLite database  
2. Run SQL queries for KPIs  
3. Export insights to CSV  
4. Visualize results with charts

---

## Project Structure

```
sales-insights-sql/
├─ README.md
├─ requirements.txt
├─ data/
│  └─ sales_data.csv
├─ src/
│  ├─ create_db.py
│  ├─ queries.sql
│  ├─ analyze_sales.py
│  └─ utils.py
└─ outputs/
   ├─ charts/
   │   ├─ revenue_by_region.png
   │   └─ monthly_sales_trend.png
   ├─ revenue_by_region.csv
   ├─ top_products_by_revenue.csv
   ├─ top_products_by_quantity.csv
   ├─ monthly_sales_trend.csv
   └─ aov_summary.csv
```

---

## Dataset

A **synthetic dataset** of 10 products sold across 4 regions (North, South, East, West) over one year.

| Column | Description |
|--------|--------------|
| order_id | Unique order identifier |
| date | Order date (YYYY-MM-DD) |
| region | Sales region |
| product | Product name |
| quantity | Quantity sold |
| unit_price | Unit price of the product |
| revenue | Calculated as `quantity × unit_price` |

Example preview:

| order_id | date       | region | product  | quantity | unit_price | revenue |
|-----------|------------|--------|-----------|-----------|-------------|----------|
| 1001 | 2024-01-01 | North | Laptop | 2 | 1050.00 | 2100.00 |
| 1001 | 2024-01-01 | North | Mouse | 1 | 23.50 | 23.50 |
| 1002 | 2024-01-01 | South | Printer | 1 | 145.00 | 145.00 |

---

## Setup & Usage

### Create Virtual Environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Create SQLite Database

```bash
python src/create_db.py --csv data/sales_data.csv --db sales.db
```

### Run SQL Analytics + Visualization

```bash
python src/analyze_sales.py --db sales.db --sql src/queries.sql --outdir outputs
```

---

## SQL Queries Summary

Inside `src/queries.sql`, five core analyses are defined:

| Query | Description |
|-------|--------------|
| **Revenue by Region** | Total revenue per region |
| **Top Products by Revenue** | Best-selling products |
| **Top Products by Quantity** | Most purchased products |
| **Monthly Sales Trend** | Revenue trend over time |
| **Average Order Value (AOV)** | Revenue per order by region |

Example SQL snippet:

```sql
SELECT region, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;
```

---

## Example Results

### Revenue by Region
<img width="1200" height="750" alt="revenue_by_region" src="https://github.com/user-attachments/assets/6b9ba0bc-1299-416d-8de4-6e49d2ed7968" />

**Insight:**  
> The West and East regions generated the highest revenues, indicating stronger customer engagement and product performance in those markets.

---

### Monthly Sales Trend
<img width="1200" height="750" alt="monthly_sales_trend" src="https://github.com/user-attachments/assets/b5a403a4-6ae2-4f1d-998c-5073ff7bb676" />

**Insight:**  
> Sales consistently rise through Q3 and Q4, showing a clear seasonal trend — possibly due to holiday promotions or end-of-year demand spikes.

---

### Top Products by Revenue

| Product | Total Revenue |
|----------|----------------|
| Laptop | $2,401,210 |
| Smartphone | $1,964,050 |
| Monitor | $801,220 |
| Printer | $543,970 |
| Desk | $415,300 |

> **Laptops and Smartphones** dominate revenue, accounting for over 50% of total sales.

---

### Average Order Value (AOV)

| Region | Total Revenue | Orders | AOV |
|--------|----------------|---------|------|
| West | 2,320,000 | 11,200 | 207.14 |
| East | 1,980,000 | 10,300 | 192.23 |
| North | 1,760,000 | 9,800 | 179.59 |
| South | 1,520,000 | 9,400 | 161.70 |

> Higher AOV in the **West** indicates customers purchase more premium or bulk items.

---

## Tools & Libraries

| Technology | Purpose |
|-------------|----------|
| **SQLite** | Lightweight SQL database |
| **Python** | Orchestration, analysis, visualization |
| **pandas** | Data manipulation & CSV I/O |
| **matplotlib** | Chart creation |
| **SQL** | Querying and data aggregation |

---

## Key Learnings

- Combine **SQL** and **Python** for real-world analytics workflows  
- Build reproducible, automated reports  
- Apply common business KPIs: revenue, trends, and AOV  
- Communicate insights effectively with visuals

---

## Example Insight Summary

> - The **West** region leads in total revenue.  
> - **Laptops** are the most profitable product category.  
> - Revenue increases significantly toward **Q4**, suggesting seasonal buying patterns.  
> - Average order values differ by region, hinting at regional purchasing behavior differences.

---

## Conclusion

**Sales Insights with SQL and Python** is a compact yet powerful example of end-to-end data analytics.  
It highlights your ability to:
- Work with databases and SQL  
- Automate reporting pipelines  
- Produce professional visuals  
- Communicate meaningful business insights  
