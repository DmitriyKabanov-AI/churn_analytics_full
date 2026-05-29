-- =====================================================
-- Таблицы для хранения сырых данных
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY,
    region VARCHAR(50),
    channel VARCHAR(50),
    device VARCHAR(50),
    plan VARCHAR(50),
    income NUMERIC(10,2),
    created_at DATE
);

CREATE TABLE IF NOT EXISTS subscriptions (
    user_id INT,
    plan VARCHAR(50),
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN
);

CREATE TABLE IF NOT EXISTS events (
    event_id INT PRIMARY KEY,
    user_id INT,
    event_type VARCHAR(50),
    timestamp TIMESTAMP,
    amount DECIMAL(10,2),
    page TEXT
);

-- =====================================================
-- Таблицы для витрин
-- =====================================================
CREATE TABLE IF NOT EXISTS retention_cohorts (
    cohort_month VARCHAR(10),
    months_diff INT,
    active_users INT,
    cohort_size INT,
    retention_rate FLOAT
);

CREATE TABLE IF NOT EXISTS rfm (
    user_id INT,
    recency INT,
    frequency INT,
    monetary DECIMAL,
    r_score VARCHAR,
    f_score VARCHAR,
    m_score VARCHAR,
    rfm_score VARCHAR
);

CREATE TABLE IF NOT EXISTS ltv (
    cohort_month VARCHAR(10),
    purchase_month VARCHAR(10),
    total_revenue DECIMAL,
    users INT,
    ltv FLOAT
);

CREATE TABLE IF NOT EXISTS daily_metrics (
    date DATE,
    dau INT,
    total_events INT,
    purchases INT,
    revenue DECIMAL,
    arpu FLOAT,
    conversion_to_purchase FLOAT
);

CREATE TABLE IF NOT EXISTS churn_by_region (region VARCHAR(50), churns INT);
CREATE TABLE IF NOT EXISTS churn_by_plan   (plan VARCHAR(50),   churns INT);
CREATE TABLE IF NOT EXISTS churn_by_channel(channel VARCHAR(50), churns INT);

-- =====================================================
-- Функция 1: Генерация тестовых данных
-- =====================================================
CREATE OR REPLACE FUNCTION generate_churn_data(
    num_users INT,
    num_events INT
)
RETURNS TEXT AS $$
DECLARE
    regions TEXT[] := ARRAY['North','South','East','West','Central'];
    plans TEXT[]   := ARRAY['Basic','Standard','Premium'];
    channels TEXT[]:= ARRAY['organic','paid_ads','referral','social'];
    devices TEXT[] := ARRAY['mobile','desktop','tablet'];
    event_types TEXT[] := ARRAY['login','purchase','view','click','churn'];
    user_id INT;
    ev_start_date TIMESTAMP;
    ev_end_date TIMESTAMP;
BEGIN
    TRUNCATE users, subscriptions, events RESTART IDENTITY CASCADE;

    INSERT INTO users (user_id, region, channel, device, plan, income, created_at)
    SELECT i,
           regions[1 + floor(random() * array_length(regions,1))],
           channels[1 + floor(random() * array_length(channels,1))],
           devices[1 + floor(random() * array_length(devices,1))],
           plans[1 + floor(random() * array_length(plans,1))],
           20000 + random() * 80000,
           CURRENT_DATE - (random() * 365)::INT
    FROM generate_series(1, num_users) AS i;

    INSERT INTO subscriptions (user_id, plan, start_date, end_date, is_active)
    SELECT u.user_id,
           u.plan,
           u.created_at,
           CASE WHEN random() < 0.3 THEN u.created_at + (random() * 180 + 30)::INT ELSE NULL END,
           random() > 0.3
    FROM users u
    WHERE random() < 0.6;

    ev_start_date := NOW() - INTERVAL '365 days';
    ev_end_date   := NOW();
    FOR i IN 1..num_events LOOP
        user_id := 1 + floor(random() * num_users);
        INSERT INTO events (event_id, user_id, event_type, timestamp, amount, page)
        VALUES (
            i,
            user_id,
            event_types[1 + floor(random() * array_length(event_types,1))],
            ev_start_date + random() * (ev_end_date - ev_start_date),
            CASE WHEN random() < 0.2 THEN 10 + random() * 490 ELSE NULL END,
            'https://example.com/' || floor(random()*100)::TEXT
        );
    END LOOP;

    RETURN format('Generated %s users and %s events', num_users, num_events);
END;
$$ LANGUAGE plpgsql;

/*-- =====================================================
-- Функция 2: Расчёт аналитических витрин (исправленная)
-- =====================================================
CREATE OR REPLACE FUNCTION compute_churn_metrics()
RETURNS TEXT AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
BEGIN
    start_time := clock_timestamp();

    -- 1. Retention cohorts
    DELETE FROM retention_cohorts;
    WITH login_events AS (
        SELECT e.user_id, u.created_at::date as reg_date, e.timestamp::date as event_date
        FROM events e JOIN users u ON e.user_id = u.user_id
        WHERE e.event_type = 'login'
    ),
    cohorts AS (
        SELECT user_id,
               DATE_TRUNC('month', reg_date)::date AS cohort_month,
               DATE_TRUNC('month', event_date)::date AS activity_month,
               EXTRACT(YEAR FROM age(event_date, reg_date))*12 + EXTRACT(MONTH FROM age(event_date, reg_date)) AS months_diff
        FROM login_events
        GROUP BY user_id, cohort_month, activity_month, months_diff
    ),
    cohort_size AS (
        SELECT cohort_month, COUNT(DISTINCT user_id) AS total_users
        FROM cohorts WHERE months_diff = 0 GROUP BY cohort_month
    ),
    retention_rates AS (
        SELECT c.cohort_month, c.months_diff,
               COUNT(DISTINCT c.user_id) AS active_users,
               cs.total_users AS cohort_size,
               ROUND(100.0 * COUNT(DISTINCT c.user_id) / cs.total_users, 2) AS retention_rate
        FROM cohorts c JOIN cohort_size cs ON c.cohort_month = cs.cohort_month
        GROUP BY c.cohort_month, c.months_diff, cs.total_users
    )
    INSERT INTO retention_cohorts (cohort_month, months_diff, active_users, cohort_size, retention_rate)
    SELECT cohort_month::text, months_diff, active_users, cohort_size, retention_rate
    FROM retention_rates ORDER BY cohort_month, months_diff;

    -- 2. RFM
    DELETE FROM rfm;
    WITH purchase_stats AS (
        SELECT user_id,
               EXTRACT(DAY FROM (NOW() - MAX(timestamp))) AS recency,
               COUNT(*) AS frequency,
               COALESCE(SUM(amount), 0) AS monetary
        FROM events WHERE event_type = 'purchase' GROUP BY user_id
    ),
    rfm_scores AS (
        SELECT user_id, recency, frequency, monetary,
               NTILE(4) OVER (ORDER BY recency DESC) AS r_score,
               NTILE(4) OVER (ORDER BY frequency ASC)  AS f_score,
               NTILE(4) OVER (ORDER BY monetary ASC)   AS m_score
        FROM purchase_stats
    )
    INSERT INTO rfm (user_id, recency, frequency, monetary, r_score, f_score, m_score, rfm_score)
    SELECT user_id, recency, frequency, monetary,
           r_score::text, f_score::text, m_score::text,
           r_score::text || f_score::text || m_score::text
    FROM rfm_scores;

    -- 3. LTV
    DELETE FROM ltv;
    WITH purchases AS (
        SELECT e.user_id, e.amount, e.timestamp::date AS purchase_date,
               u.created_at::date AS reg_date
        FROM events e JOIN users u ON e.user_id = u.user_id
        WHERE e.event_type = 'purchase'
    ),
    cohort_revenue AS (
        SELECT DATE_TRUNC('month', reg_date)::date AS cohort_month,
               DATE_TRUNC('month', purchase_date)::date AS purchase_month,
               COUNT(DISTINCT user_id) AS paying_users,
               SUM(amount) AS total_revenue
        FROM purchases
        GROUP BY cohort_month, purchase_month
    ),
    cohort_users AS (
        SELECT DATE_TRUNC('month', created_at)::date AS cohort_month,
               COUNT(*) AS total_users
        FROM users GROUP BY cohort_month
    )
    INSERT INTO ltv (cohort_month, purchase_month, total_revenue, users, ltv)
    SELECT cr.cohort_month::text, cr.purchase_month::text,
           cr.total_revenue, cu.total_users,
           ROUND(cr.total_revenue / NULLIF(cu.total_users, 0), 2)
    FROM cohort_revenue cr JOIN cohort_users cu ON cr.cohort_month = cu.cohort_month
    ORDER BY cr.cohort_month, cr.purchase_month;

    -- 4. Daily metrics
    DELETE FROM daily_metrics;
    WITH daily_agg AS (
        SELECT timestamp::date AS date,
               COUNT(DISTINCT user_id) AS dau,
               COUNT(*) AS total_events,
               SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases,
               COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN amount ELSE 0 END), 0) AS revenue
        FROM events GROUP BY date
    )
    INSERT INTO daily_metrics (date, dau, total_events, purchases, revenue, arpu, conversion_to_purchase)
    SELECT date, dau, total_events, purchases, revenue,
           ROUND(revenue::numeric / NULLIF(dau, 0), 2) AS arpu,
           ROUND(100.0 * purchases / NULLIF(dau, 0), 2) AS conversion_to_purchase
    FROM daily_agg;

    -- 5. Отток по категориям (исправлено)
    DELETE FROM churn_by_region;
    DELETE FROM churn_by_plan;
    DELETE FROM churn_by_channel;
    
    CREATE TEMP TABLE churned_temp AS
    SELECT s.user_id, u.region, u.channel, u.plan
    FROM subscriptions s
    JOIN users u ON s.user_id = u.user_id
    WHERE s.end_date IS NOT NULL;
    
    INSERT INTO churn_by_region
    SELECT region, COUNT(*) FROM churned_temp GROUP BY region;
    
    INSERT INTO churn_by_plan
    SELECT plan, COUNT(*) FROM churned_temp GROUP BY plan;
    
    INSERT INTO churn_by_channel
    SELECT channel, COUNT(*) FROM churned_temp GROUP BY channel;
    
    DROP TABLE churned_temp;

    end_time := clock_timestamp();
    RETURN format('Metrics computed in %s ms', EXTRACT(EPOCH FROM (end_time - start_time)) * 1000);
END;
$$ LANGUAGE plpgsql;*/