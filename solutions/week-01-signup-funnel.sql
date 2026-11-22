-- Q1 ------------------------------------------------------------
SELECT acquisition_channel,
       COUNT(*) AS visitors
FROM users
GROUP BY acquisition_channel
ORDER BY visitors DESC;
-- Q2 ------------------------------------------------------------
SELECT event_name,
       COUNT(*)                AS total_events,
       COUNT(DISTINCT user_id) AS unique_users
FROM events
GROUP BY event_name
ORDER BY unique_users DESC;
-- Q3 ------------------------------------------------------------
SELECT u.device,
       COUNT(DISTINCT u.user_id) AS visitors,
       COUNT(DISTINCT e.user_id) AS signups,
       ROUND(100.0 * COUNT(DISTINCT e.user_id) / COUNT(DISTINCT u.user_id), 1) AS signup_rate_pct
FROM users u
LEFT JOIN events e
       ON e.user_id = u.user_id
      AND e.event_name = 'signup'
GROUP BY u.device
ORDER BY signup_rate_pct DESC;
-- Q4 ------------------------------------------------------------
SELECT u.acquisition_channel,
       COUNT(DISTINCT CASE WHEN e.event_name = 'signup'         THEN u.user_id END) AS signups,
       COUNT(DISTINCT CASE WHEN e.event_name = 'first_purchase' THEN u.user_id END) AS paying_customers,
       ROUND(100.0
             * COUNT(DISTINCT CASE WHEN e.event_name = 'first_purchase' THEN u.user_id END)
             / COUNT(DISTINCT CASE WHEN e.event_name = 'signup'         THEN u.user_id END), 1) AS signup_to_paying_pct
FROM users u
JOIN events e ON e.user_id = u.user_id
GROUP BY u.acquisition_channel
ORDER BY signup_to_paying_pct DESC;
-- Q5 ------------------------------------------------------------
SELECT u.user_id,
       u.country,
       u.acquisition_channel,
       MIN(e.event_at) AS signup_at
FROM users u
JOIN events e ON e.user_id = u.user_id
WHERE e.event_name = 'signup'
  AND e.event_at >= '2026-11-01'
  AND u.user_id NOT IN (SELECT user_id
                        FROM events
                        WHERE event_name = 'onboarding_complete')
GROUP BY u.user_id, u.country, u.acquisition_channel
ORDER BY signup_at DESC;
-- Q6 ------------------------------------------------------------
SELECT CASE WHEN s.signup_at < '2026-10-15' THEN '1. before v2' ELSE '2. after v2' END AS period,
       COUNT(*) AS signups,
       SUM(CASE WHEN s.user_id IN (SELECT user_id FROM events
                                   WHERE event_name = 'onboarding_complete')
                THEN 1 ELSE 0 END) AS completed_onboarding,
       ROUND(100.0 * SUM(CASE WHEN s.user_id IN (SELECT user_id FROM events
                                                 WHERE event_name = 'onboarding_complete')
                              THEN 1 ELSE 0 END) / COUNT(*), 1) AS onboarding_rate_pct
FROM (SELECT user_id, MIN(event_at) AS signup_at
      FROM events
      WHERE event_name = 'signup'
      GROUP BY user_id) AS s
WHERE s.signup_at < '2026-11-09'
GROUP BY period
ORDER BY period;
-- Q7 ------------------------------------------------------------
SELECT purchase_date,
       new_customers,
       SUM(new_customers) OVER (ORDER BY purchase_date) AS cumulative_customers
FROM (SELECT DATE(event_at) AS purchase_date,
             COUNT(DISTINCT user_id) AS new_customers
      FROM events
      WHERE event_name = 'first_purchase'
      GROUP BY DATE(event_at)) AS daily
ORDER BY purchase_date;
-- Q8 ------------------------------------------------------------
SELECT step,
       event_name,
       users,
       ROUND(100.0 * users / FIRST_VALUE(users) OVER (ORDER BY step), 1) AS pct_of_visitors,
       ROUND(100.0 * users / LAG(users) OVER (ORDER BY step), 1)        AS pct_of_previous_step
FROM (SELECT CASE event_name
               WHEN 'landing_view'        THEN 1
               WHEN 'signup'              THEN 2
               WHEN 'onboarding_complete' THEN 3
               WHEN 'first_purchase'      THEN 4
             END AS step,
             event_name,
             COUNT(DISTINCT user_id) AS users
      FROM events
      GROUP BY event_name) AS funnel
ORDER BY step;
