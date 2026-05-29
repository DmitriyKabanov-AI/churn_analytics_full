CREATE OR REPLACE FUNCTION compute_daily_metrics()
RETURNS TEXT AS $$
BEGIN
    DELETE FROM daily_metrics;
    
    INSERT INTO daily_metrics (date, dau, total_events, purchases, revenue, arpu, conversion_to_purchase)
    SELECT 
        timestamp::date AS date,
        COUNT(DISTINCT user_id) AS dau,
        COUNT(*) AS total_events,
        SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases,
        COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN amount ELSE 0 END), 0) AS revenue,
        ROUND(COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN amount ELSE 0 END), 0)::numeric / NULLIF(COUNT(DISTINCT user_id), 0), 2) AS arpu,
        ROUND(100.0 * SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT user_id), 0), 2) AS conversion_to_purchase
    FROM events
    GROUP BY date
    ORDER BY date;
    
    RETURN format('Daily metrics computed: %s rows inserted', (SELECT COUNT(*) FROM daily_metrics));
END;
$$ LANGUAGE plpgsql;