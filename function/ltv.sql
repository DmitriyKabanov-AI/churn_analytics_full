CREATE OR REPLACE FUNCTION compute_ltv()
RETURNS TEXT AS $$
BEGIN
    DELETE FROM ltv;
    
    WITH purchases AS (
        SELECT e.user_id, e.amount, e.timestamp::date AS purchase_date,
               u.created_at::date AS reg_date
        FROM events e
        JOIN users u ON e.user_id = u.user_id
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
        FROM users
        GROUP BY cohort_month
    )
    INSERT INTO ltv (cohort_month, purchase_month, total_revenue, users, ltv)
    SELECT cr.cohort_month::text,
           cr.purchase_month::text,
           cr.total_revenue,
           cu.total_users,
           ROUND(cr.total_revenue / NULLIF(cu.total_users, 0), 2)
    FROM cohort_revenue cr
    JOIN cohort_users cu ON cr.cohort_month = cu.cohort_month
    ORDER BY cr.cohort_month, cr.purchase_month;
    
    RETURN format('LTV computed: %s rows', (SELECT COUNT(*) FROM ltv));
END;
$$ LANGUAGE plpgsql;