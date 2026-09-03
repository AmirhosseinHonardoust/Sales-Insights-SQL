-- Core analytics for Sales Insights
--
-- Each statement is preceded by a "-- name: <label>" comment. This label is
-- what analyze_sales.py uses to name the output CSV and to decide which
-- chart (if any) to render — it is NOT inferred from statement position, so
-- queries can be reordered or added without breaking the pipeline.

-- name: revenue_by_region
-- 1) Revenue by region
SELECT region, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;

-- name: top_products_by_revenue
-- 2) Top products by revenue
SELECT product, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY product
ORDER BY total_revenue DESC
LIMIT 10;

-- name: top_products_by_quantity
-- 3) Top products by quantity
SELECT product, SUM(quantity) AS total_qty
FROM sales
GROUP BY product
ORDER BY total_qty DESC
LIMIT 10;

-- name: monthly_sales_trend
-- 4) Monthly sales trend
SELECT strftime('%Y-%m', date) AS month, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY month
ORDER BY month ASC;

-- name: aov_summary
-- 5) Average Order Value (AOV) by region
WITH region_rev AS (
  SELECT region, SUM(revenue) AS rev, COUNT(DISTINCT order_id) AS orders
  FROM sales
  GROUP BY region
)
SELECT region,
       ROUND(rev, 2) AS total_revenue,
       orders AS n_orders,
       ROUND(rev * 1.0 / orders, 2) AS aov
FROM region_rev
ORDER BY aov DESC;
