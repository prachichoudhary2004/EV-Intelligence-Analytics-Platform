-- EV Intelligence Analytics - Complex SQL Queries
-- Production-ready queries for business intelligence and KPI analysis

-- ============================================
-- TOP PERFORMING STATES ANALYSIS
-- ============================================

-- Top 10 states by EV sales volume
SELECT 
    s.state_name,
    SUM(es.sales_amount) as total_sales,
    SUM(es.revenue) as total_revenue,
    COUNT(DISTINCT es.manufacturer_id) as manufacturer_count,
    AVG(es.market_share) as avg_market_share,
    RANK() OVER (ORDER BY SUM(es.sales_amount) DESC) as sales_rank
FROM ev_sales es
JOIN states s ON es.state_id = s.state_id
GROUP BY s.state_name
ORDER BY total_sales DESC
LIMIT 10;

-- States with highest EV penetration rates
SELECT 
    s.state_name,
    s.population,
    AVG(mm.ev_penetration_rate) as avg_penetration_rate,
    SUM(es.sales_amount) as total_ev_sales,
    (SUM(es.sales_amount) * 1000.0 / s.population) as evs_per_1000_people,
    cs.total_charging_stations,
    cs.total_charging_stations * 1000.0 / SUM(es.sales_amount) as stations_per_1000_evs
FROM states s
LEFT JOIN ev_sales es ON s.state_id = es.state_id
LEFT JOIN market_metrics mm ON s.state_id = mm.state_id
LEFT JOIN (
    SELECT state_id, SUM(total_stations) as total_charging_stations
    FROM charging_stations
    GROUP BY state_id
) cs ON s.state_id = cs.state_id
GROUP BY s.state_name, s.population, cs.total_charging_stations
ORDER BY avg_penetration_rate DESC;

-- ============================================
-- MANUFACTURER RANKINGS
-- ============================================

-- National manufacturer rankings
SELECT 
    m.manufacturer_name,
    SUM(es.sales_amount) as total_sales,
    SUM(es.revenue) as total_revenue,
    AVG(es.price_avg) as avg_vehicle_price,
    COUNT(DISTINCT es.state_id) as states_presence,
    AVG(es.market_share) as avg_market_share,
    RANK() OVER (ORDER BY SUM(es.sales_amount) DESC) as national_rank,
    SUM(es.sales_amount) * 100.0 / (SELECT SUM(sales_amount) FROM ev_sales) as market_share_pct
FROM ev_sales es
JOIN manufacturers m ON es.manufacturer_id = m.manufacturer_id
GROUP BY m.manufacturer_name
ORDER BY total_sales DESC;

-- Manufacturer performance by state
SELECT 
    s.state_name,
    m.manufacturer_name,
    SUM(es.sales_amount) as total_sales,
    SUM(es.revenue) as total_revenue,
    AVG(es.market_share) as avg_market_share,
    RANK() OVER (PARTITION BY s.state_name ORDER BY SUM(es.sales_amount) DESC) as state_rank,
    LAG(SUM(es.sales_amount)) OVER (PARTITION BY m.manufacturer_id ORDER BY s.state_name) as prev_state_sales,
    SUM(es.sales_amount) - LAG(SUM(es.sales_amount)) OVER (PARTITION BY m.manufacturer_id ORDER BY s.state_name) as sales_diff
FROM ev_sales es
JOIN states s ON es.state_id = s.state_id
JOIN manufacturers m ON es.manufacturer_id = m.manufacturer_id
GROUP BY s.state_name, m.manufacturer_name
ORDER BY s.state_name, state_rank;

-- ============================================
-- MONTHLY GROWTH TRENDS
-- ============================================

-- Month-over-month growth analysis
WITH monthly_sales AS (
    SELECT 
        t.year,
        t.month,
        t.month_name,
        SUM(es.sales_amount) as total_sales,
        SUM(es.revenue) as total_revenue,
        COUNT(DISTINCT es.state_id) as active_states
    FROM ev_sales es
    JOIN time_dimension t ON es.date_id = t.date_id
    GROUP BY t.year, t.month, t.month_name
),
monthly_growth AS (
    SELECT 
        year,
        month,
        month_name,
        total_sales,
        total_revenue,
        active_states,
        LAG(total_sales) OVER (ORDER BY year, month) as prev_month_sales,
        LAG(total_revenue) OVER (ORDER BY year, month) as prev_month_revenue,
        (total_sales - LAG(total_sales) OVER (ORDER BY year, month)) * 100.0 / 
            LAG(total_sales) OVER (ORDER BY year, month) as sales_growth_pct,
        (total_revenue - LAG(total_revenue) OVER (ORDER BY year, month)) * 100.0 / 
            LAG(total_revenue) OVER (ORDER BY year, month) as revenue_growth_pct
    FROM monthly_sales
)
SELECT 
    year,
    month,
    month_name,
    total_sales,
    total_revenue,
    active_states,
    sales_growth_pct,
    revenue_growth_pct,
    CASE 
        WHEN sales_growth_pct > 10 THEN 'High Growth'
        WHEN sales_growth_pct > 0 THEN 'Moderate Growth'
        WHEN sales_growth_pct > -5 THEN 'Stable'
        ELSE 'Declining'
    END as growth_category
FROM monthly_growth
ORDER BY year, month;

-- Quarterly performance trends
SELECT 
    t.year,
    t.quarter,
    SUM(es.sales_amount) as quarterly_sales,
    SUM(es.revenue) as quarterly_revenue,
    COUNT(DISTINCT es.state_id) as active_states,
    AVG(es.market_share) as avg_market_share,
    SUM(es.sales_amount) * 100.0 / LAG(SUM(es.sales_amount)) OVER (ORDER BY t.year, t.quarter) - 100 as qoq_growth_pct
FROM ev_sales es
JOIN time_dimension t ON es.date_id = t.date_id
GROUP BY t.year, t.quarter
ORDER BY t.year, t.quarter;

-- ============================================
-- MARKET SHARE ANALYSIS
-- ============================================

-- Market share by manufacturer over time
SELECT 
    t.year,
    t.month,
    m.manufacturer_name,
    SUM(es.sales_amount) as monthly_sales,
    SUM(es.sales_amount) * 100.0 / SUM(SUM(es.sales_amount)) OVER (PARTITION BY t.year, t.month) as market_share_pct,
    SUM(es.sales_amount) * 100.0 / SUM(SUM(es.sales_amount)) OVER (PARTITION BY m.manufacturer_id ORDER BY t.year, t.month 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as cumulative_share
FROM ev_sales es
JOIN time_dimension t ON es.date_id = t.date_id
JOIN manufacturers m ON es.manufacturer_id = m.manufacturer_id
GROUP BY t.year, t.month, m.manufacturer_name
ORDER BY t.year, t.month, market_share_pct DESC;

-- Vehicle category market share
SELECT 
    vt.category,
    vt.vehicle_type,
    SUM(es.sales_amount) as total_sales,
    SUM(es.revenue) as total_revenue,
    AVG(es.price_avg) as avg_price,
    SUM(es.sales_amount) * 100.0 / (SELECT SUM(sales_amount) FROM ev_sales) as market_share_pct,
    AVG(es.battery_capacity) as avg_battery_capacity,
    AVG(es.charging_time) as avg_charging_time
FROM ev_sales es
JOIN vehicle_types vt ON es.vehicle_type_id = vt.vehicle_type_id
GROUP BY vt.category, vt.vehicle_type
ORDER BY market_share_pct DESC;

-- ============================================
-- YEAR-OVER-YEAR GROWTH
-- ============================================

-- YoY growth comparison
WITH yearly_sales AS (
    SELECT 
        t.year,
        SUM(es.sales_amount) as total_sales,
        SUM(es.revenue) as total_revenue,
        COUNT(DISTINCT es.state_id) as active_states,
        COUNT(DISTINCT es.manufacturer_id) as active_manufacturers
    FROM ev_sales es
    JOIN time_dimension t ON es.date_id = t.date_id
    GROUP BY t.year
)
SELECT 
    year,
    total_sales,
    total_revenue,
    active_states,
    active_manufacturers,
    LAG(total_sales) OVER (ORDER BY year) as prev_year_sales,
    LAG(total_revenue) OVER (ORDER BY year) as prev_year_revenue,
    (total_sales - LAG(total_sales) OVER (ORDER BY year)) * 100.0 / 
        LAG(total_sales) OVER (ORDER BY year) as sales_yoy_growth_pct,
    (total_revenue - LAG(total_revenue) OVER (ORDER BY year)) * 100.0 / 
        LAG(total_revenue) OVER (ORDER BY year) as revenue_yoy_growth_pct
FROM yearly_sales
ORDER BY year;

-- State-wise YoY growth
SELECT 
    s.state_name,
    t.year,
    SUM(es.sales_amount) as yearly_sales,
    LAG(SUM(es.sales_amount)) OVER (PARTITION BY s.state_name ORDER BY t.year) as prev_year_sales,
    (SUM(es.sales_amount) - LAG(SUM(es.sales_amount)) OVER (PARTITION BY s.state_name ORDER BY t.year)) * 100.0 / 
        LAG(SUM(es.sales_amount)) OVER (PARTITION BY s.state_name ORDER BY t.year) as yoy_growth_pct,
    RANK() OVER (PARTITION BY t.year ORDER BY SUM(es.sales_amount) DESC) as state_rank_yearly
FROM ev_sales es
JOIN states s ON es.state_id = s.state_id
JOIN time_dimension t ON es.date_id = t.date_id
GROUP BY s.state_name, t.year
ORDER BY t.year, yoy_growth_pct DESC;

-- ============================================
-- CHARGING INFRASTRUCTURE ANALYSIS
-- ============================================

-- Charging infrastructure efficiency
SELECT 
    s.state_name,
    SUM(cs.total_stations) as total_stations,
    SUM(cs.fast_chargers) as total_fast_chargers,
    SUM(cs.slow_chargers) as total_slow_chargers,
    AVG(cs.utilization_rate) as avg_utilization_rate,
    AVG(cs.avg_power_kw) as avg_power_capacity,
    SUM(cs.total_power_capacity) as total_power_capacity,
    SUM(es.sales_amount) as total_ev_sales,
    SUM(cs.total_stations) * 1000.0 / SUM(es.sales_amount) as stations_per_1000_evs,
    AVG(cs.fast_charger_ratio) as avg_fast_charger_ratio
FROM charging_stations cs
JOIN states s ON cs.state_id = s.state_id
LEFT JOIN ev_sales es ON s.state_id = es.state_id
GROUP BY s.state_name
ORDER BY total_ev_sales DESC;

-- Charging station utilization trends
SELECT 
    cs.city,
    s.state_name,
    cs.total_stations,
    cs.fast_chargers,
    cs.utilization_rate,
    cs.installation_age_days,
    cs.total_power_capacity,
    CASE 
        WHEN cs.utilization_rate > 0.8 THEN 'High Utilization'
        WHEN cs.utilization_rate > 0.6 THEN 'Moderate Utilization'
        WHEN cs.utilization_rate > 0.4 THEN 'Low Utilization'
        ELSE 'Underutilized'
    END as utilization_category
FROM charging_stations cs
JOIN states s ON cs.state_id = s.state_id
ORDER BY cs.utilization_rate DESC;

-- ============================================
-- KPI DASHBOARD QUERIES
-- ============================================

-- Executive KPI summary
SELECT 
    COUNT(DISTINCT es.state_id) as total_states_active,
    COUNT(DISTINCT es.manufacturer_id) as total_manufacturers,
    SUM(es.sales_amount) as total_ev_sales,
    SUM(es.revenue) as total_revenue,
    AVG(es.price_avg) as avg_vehicle_price,
    AVG(mm.ev_penetration_rate) as avg_penetration_rate,
    SUM(cs.total_stations) as total_charging_stations,
    AVG(cs.utilization_rate) as avg_station_utilization
FROM ev_sales es
LEFT JOIN market_metrics mm ON es.state_id = mm.state_id
LEFT JOIN charging_stations cs ON es.state_id = cs.state_id;

-- Top emerging markets (high growth potential)
SELECT 
    s.state_name,
    AVG(mm.ev_penetration_rate) as current_penetration,
    AVG(mm.market_potential_score) as market_potential,
    SUM(es.sales_amount) as current_sales,
    AVG(mm.gdp_per_capita) as avg_income,
    SUM(cs.total_stations) as charging_infrastructure,
    (AVG(mm.market_potential_score) * AVG(mm.gdp_per_capita) / 1000) as growth_score
FROM states s
LEFT JOIN ev_sales es ON s.state_id = es.state_id
LEFT JOIN market_metrics mm ON s.state_id = mm.state_id
LEFT JOIN charging_stations cs ON s.state_id = cs.state_id
GROUP BY s.state_name
ORDER BY growth_score DESC
LIMIT 10;
