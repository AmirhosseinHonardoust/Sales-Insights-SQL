-- Core analytics for Sales Insights

-- 1) Revenue by region
SELECT region, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;

-- 2) Top products by revenue
SELECT product, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY product
ORDER BY total_revenue DESC
LIMIT 10;

-- 3) Top products by quantity
SELECT product, SUM(quantity) AS total_qty
FROM sales
GROUP BY product
ORDER BY total_qty DESC
LIMIT 10;

-- 4) Monthly sales trend
SELECT strftime('%Y-%m', date) AS month, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY month
ORDER BY month ASC;

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
