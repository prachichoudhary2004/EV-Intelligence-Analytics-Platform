{% snapshot manufacturer_scd2_snapshot %}

{{
  config(
    target_schema='snapshots',
    unique_key='manufacturer',
    strategy='timestamp',
    updated_at='last_updated'
  )
}}

SELECT
    manufacturer,
    sales_amount,
    revenue,
    market_share,
    current_timestamp() AS last_updated
FROM {{ source('silver', 'ev_sales_silver') }}

{% endsnapshot %}
