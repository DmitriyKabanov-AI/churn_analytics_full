CREATE OR REPLACE FUNCTION compute_retention()
RETURNS TEXT AS $$
BEGIN
    DELETE FROM retention_cohorts;
    
    WITH login_events AS (
        SELECT e.user_id, u.created_at::date AS reg_date, e.timestamp::date AS event_date
        FROM events e
        JOIN users u ON e.user_id = u.user_id
        WHERE e.event_type = 'login'
    ),
    cohorts AS (
        SELECT user_id,
               DATE_TRUNC('month', reg_date)::date AS cohort_month,
               DATE_TRUNC('month', event_date)::date AS activity_month,
               (EXTRACT(YEAR FROM age(event_date, reg_date)) * 12 +
                EXTRACT(MONTH FROM age(event_date, reg_date))) AS months_diff
        FROM login_events
        GROUP BY user_id, cohort_month, activity_month, months_diff
    ),
    cohort_size AS (
        SELECT cohort_month, COUNT(DISTINCT user_id) AS total_users
        FROM cohorts
        WHERE months_diff = 0
        GROUP BY cohort_month
    ),
    retention_rates AS (
        SELECT c.cohort_month,
               c.months_diff,
               COUNT(DISTINCT c.user_id) AS active_users,
               cs.total_users AS cohort_size,
               ROUND(100.0 * COUNT(DISTINCT c.user_id) / cs.total_users, 2) AS retention_rate
        FROM cohorts c
        JOIN cohort_size cs ON c.cohort_month = cs.cohort_month
        GROUP BY c.cohort_month, c.months_diff, cs.total_users
    )
    INSERT INTO retention_cohorts (cohort_month, months_diff, active_users, cohort_size, retention_rate)
    SELECT cohort_month::text, months_diff, active_users, cohort_size, retention_rate
    FROM retention_rates
    ORDER BY cohort_month, months_diff;
    
    RETURN format('Retention cohorts computed: %s rows', (SELECT COUNT(*) FROM retention_cohorts));
END;
$$ LANGUAGE plpgsql;