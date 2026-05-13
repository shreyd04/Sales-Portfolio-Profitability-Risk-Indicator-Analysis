SELECT 
    segment,
    AVG(discount) as avg_discount,
    SUM(profit) / SUM(sales) * 100 as margin_percentage,
    CASE 
        WHEN SUM(profit) < 0 THEN 'High Risk'
        ELSE 'Stable'
    END as risk_status
FROM orders
WHERE segment = 'Home Office'
GROUP BY segment;

-- 2. Detecting High-Discount/Low-Profit Clusters (Margin Leakage)
SELECT 
    sub_category,
    COUNT(order_id) as total_orders,
    SUM(CASE WHEN discount > 0.2 THEN 1 ELSE 0 END) as high_discount_orders,
    SUM(profit) as net_profit
FROM orders
GROUP BY sub_category
HAVING SUM(profit) < 0
ORDER BY net_profit ASC;