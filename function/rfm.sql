CREATE OR REPLACE FUNCTION compute_rfm()
RETURNS TEXT AS $$
BEGIN
    DELETE FROM rfm;
    
    WITH purchase_stats AS (
        SELECT user_id,
               EXTRACT(DAY FROM (NOW() - MAX(timestamp))) AS recency,
               COUNT(*) AS frequency,
               COALESCE(SUM(amount), 0) AS monetary
        FROM events
        WHERE event_type = 'purchase'
        GROUP BY user_id
    ),
    rfm_scores AS (
        SELECT user_id,
               recency,
               frequency,
               monetary,
               NTILE(4) OVER (ORDER BY recency DESC) AS r_score,
               NTILE(4) OVER (ORDER BY frequency ASC)  AS f_score,
               NTILE(4) OVER (ORDER BY monetary ASC)   AS m_score
        FROM purchase_stats
    )
    INSERT INTO rfm (user_id, recency, frequency, monetary, r_score, f_score, m_score, rfm_score)
    SELECT user_id,
           recency,
           frequency,
           monetary,
           r_score::text,
           f_score::text,
           m_score::text,
           r_score::text || f_score::text || m_score::text AS rfm_score
    FROM rfm_scores;
    
    RETURN format('RFM computed: %s users', (SELECT COUNT(*) FROM rfm));
END;
$$ LANGUAGE plpgsql;