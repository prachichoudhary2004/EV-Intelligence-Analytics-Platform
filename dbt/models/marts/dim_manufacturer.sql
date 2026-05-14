{{ config(materialized='table') }}

SELECT
    manufacturer,
    SUM(sales_amount) as total_sales,
    SUM(revenue) as total_revenue,
    AVG(market_share) as avg_market_share,
    CURRENT_TIMESTAMP() as processed_at
FROM {{ ref('stg_ev_sales') }}
GROUP BY 1
