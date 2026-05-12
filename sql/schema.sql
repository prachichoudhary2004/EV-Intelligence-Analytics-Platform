-- EV Intelligence Analytics Database Schema
-- Production-ready database structure for EV market analysis

-- States dimension table
CREATE TABLE states (
    state_id INT PRIMARY KEY,
    state_name VARCHAR(50) NOT NULL UNIQUE,
    state_code CHAR(2) NOT NULL UNIQUE,
    region VARCHAR(20),
    population BIGINT,
    gdp_per_capita DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Manufacturers dimension table
CREATE TABLE manufacturers (
    manufacturer_id INT PRIMARY KEY,
    manufacturer_name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(50),
    founded_year INT,
    market_cap DECIMAL(15,2),
    ev_focus BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Vehicle types dimension table
CREATE TABLE vehicle_types (
    vehicle_type_id INT PRIMARY KEY,
    vehicle_type VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Time dimension table
CREATE TABLE time_dimension (
    date_id DATE PRIMARY KEY,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20),
    day_of_week INT,
    day_name VARCHAR(20),
    is_weekend BOOLEAN,
    is_holiday BOOLEAN DEFAULT FALSE,
    fiscal_year INT,
    fiscal_quarter INT
);

-- Charging stations fact table
CREATE TABLE charging_stations (
    station_id INT PRIMARY KEY AUTO_INCREMENT,
    state_id INT,
    city VARCHAR(100),
    total_stations INT,
    fast_chargers INT,
    slow_chargers INT,
    avg_power_kw DECIMAL(8,2),
    utilization_rate DECIMAL(5,4),
    date_installed DATE,
    installation_age_days INT,
    fast_charger_ratio DECIMAL(5,4),
    total_power_capacity DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(state_id)
);

-- EV sales fact table
CREATE TABLE ev_sales (
    sales_id INT PRIMARY KEY AUTO_INCREMENT,
    date_id DATE,
    state_id INT,
    manufacturer_id INT,
    vehicle_type_id INT,
    sales_amount INT,
    price_min DECIMAL(10,2),
    price_max DECIMAL(10,2),
    price_avg DECIMAL(10,2),
    battery_capacity DECIMAL(8,2),
    charging_time DECIMAL(6,2),
    market_share DECIMAL(8,6),
    revenue DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (date_id) REFERENCES time_dimension(date_id),
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id),
    FOREIGN KEY (vehicle_type_id) REFERENCES vehicle_types(vehicle_type_id)
);

-- Market metrics fact table
CREATE TABLE market_metrics (
    metric_id INT PRIMARY KEY AUTO_INCREMENT,
    date_id DATE,
    state_id INT,
    total_population BIGINT,
    ev_penetration_rate DECIMAL(8,6),
    gdp_per_capita DECIMAL(12,2),
    gasoline_price DECIMAL(8,4),
    incentives_available BOOLEAN,
    charging_infrastructure_score DECIMAL(5,4),
    ev_vehicles_count DECIMAL(12,2),
    market_potential_score DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (date_id) REFERENCES time_dimension(date_id),
    FOREIGN KEY (state_id) REFERENCES states(state_id)
);

-- Aggregated monthly sales view
CREATE VIEW monthly_sales_summary AS
SELECT 
    t.year,
    t.month,
    t.month_name,
    s.state_name,
    m.manufacturer_name,
    vt.vehicle_type,
    SUM(es.sales_amount) as total_sales,
    SUM(es.revenue) as total_revenue,
    AVG(es.market_share) as avg_market_share,
    AVG(es.price_avg) as avg_price,
    AVG(es.battery_capacity) as avg_battery_capacity
FROM ev_sales es
JOIN time_dimension t ON es.date_id = t.date_id
JOIN states s ON es.state_id = s.state_id
JOIN manufacturers m ON es.manufacturer_id = m.manufacturer_id
JOIN vehicle_types vt ON es.vehicle_type_id = vt.vehicle_type_id
GROUP BY t.year, t.month, t.month_name, s.state_name, m.manufacturer_name, vt.vehicle_type;

-- Manufacturer performance view
CREATE VIEW manufacturer_performance AS
SELECT 
    m.manufacturer_name,
    s.state_name,
    SUM(es.sales_amount) as total_sales,
    SUM(es.revenue) as total_revenue,
    AVG(es.market_share) as avg_market_share,
    COUNT(DISTINCT es.date_id) as months_active,
    RANK() OVER (PARTITION BY s.state_name ORDER BY SUM(es.sales_amount) DESC) as state_rank,
    RANK() OVER (ORDER BY SUM(es.sales_amount) DESC) as national_rank
FROM ev_sales es
JOIN states s ON es.state_id = s.state_id
JOIN manufacturers m ON es.manufacturer_id = m.manufacturer_id
GROUP BY m.manufacturer_name, s.state_name;

-- State market analysis view
CREATE VIEW state_market_analysis AS
SELECT 
    s.state_name,
    s.population,
    s.gdp_per_capita,
    SUM(es.sales_amount) as total_ev_sales,
    SUM(es.revenue) as total_ev_revenue,
    AVG(mm.ev_penetration_rate) as avg_penetration_rate,
    cs.total_stations,
    cs.fast_chargers,
    cs.avg_utilization_rate,
    SUM(es.sales_amount) * 1000.0 / s.population as evs_per_1000_people,
    cs.total_stations * 1000.0 / (SUM(es.sales_amount)) as stations_per_1000_evs
FROM states s
LEFT JOIN ev_sales es ON s.state_id = es.state_id
LEFT JOIN market_metrics mm ON s.state_id = mm.state_id
LEFT JOIN (
    SELECT 
        state_id, 
        SUM(total_stations) as total_stations,
        SUM(fast_chargers) as fast_chargers,
        AVG(utilization_rate) as avg_utilization_rate
    FROM charging_stations 
    GROUP BY state_id
) cs ON s.state_id = cs.state_id
GROUP BY s.state_name, s.population, s.gdp_per_capita, cs.total_stations, 
         cs.fast_chargers, cs.avg_utilization_rate;

-- Create indexes for performance optimization
CREATE INDEX idx_ev_sales_date ON ev_sales(date_id);
CREATE INDEX idx_ev_sales_state ON ev_sales(state_id);
CREATE INDEX idx_ev_sales_manufacturer ON ev_sales(manufacturer_id);
CREATE INDEX idx_ev_sales_date_state ON ev_sales(date_id, state_id);
CREATE INDEX idx_charging_stations_state ON charging_stations(state_id);
CREATE INDEX idx_market_metrics_date_state ON market_metrics(date_id, state_id);
CREATE INDEX idx_time_dimension_year_month ON time_dimension(year, month);
