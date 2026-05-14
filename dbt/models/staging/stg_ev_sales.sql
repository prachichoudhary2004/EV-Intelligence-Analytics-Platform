SELECT
    CAST(date AS DATE) as date,
    state,
    manufacturer,
    CAST(sales_amount AS INT) as sales_amount,
    CAST(revenue AS FLOAT) as revenue,
    vehicle_category
FROM {{ source('silver', 'ev_sales_silver') }}
