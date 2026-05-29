CREATE OR REPLACE FUNCTION compute_churn_categories()
RETURNS TEXT AS $$
BEGIN
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
    
    RETURN format('Churn categories computed: region=%s, plan=%s, channel=%s',
                  (SELECT COUNT(*) FROM churn_by_region),
                  (SELECT COUNT(*) FROM churn_by_plan),
                  (SELECT COUNT(*) FROM churn_by_channel));
END;
$$ LANGUAGE plpgsql;