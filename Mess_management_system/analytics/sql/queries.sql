-- ====================================================================
-- Mess Operations & Demand Analytics - Advanced SQL Portfolio Queries
-- Demonstrating: CTEs, Window Functions, Aggregations, Joins & Subqueries
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: 7-Day Rolling Moving Average Attendance by Meal Type
-- Business Impact: Smooths out daily volatility (e.g. weekend dips) to
-- provide procurement teams with an accurate rolling demand forecast.
-- --------------------------------------------------------------------
SELECT 
    meal_date,
    day_name,
    meal_type,
    actual_headcount,
    ROUND(
        AVG(actual_headcount) OVER (
            PARTITION BY meal_type 
            ORDER BY meal_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 1
    ) AS rolling_7day_avg_attendance,
    ROUND(
        actual_headcount - AVG(actual_headcount) OVER (
            PARTITION BY meal_type 
            ORDER BY meal_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 1
    ) AS variance_from_trend
FROM menu_and_waste
ORDER BY meal_date DESC, meal_type;


-- --------------------------------------------------------------------
-- QUERY 2: Food Waste & Financial Loss Leaderboard by Menu Item
-- Business Impact: Identifies dishes that generate disproportionate 
-- waste and loss to optimize menu rotation or reduce batch sizing.
-- --------------------------------------------------------------------
WITH DishMetrics AS (
    SELECT 
        menu_item,
        category,
        COUNT(*) AS times_served,
        SUM(portions_prepared) AS total_prepared,
        SUM(portions_wasted) AS total_wasted,
        ROUND(SUM(food_wasted_kg), 2) AS total_waste_kg,
        ROUND(SUM(financial_loss_inr), 2) AS total_financial_loss,
        ROUND(AVG(portions_wasted::NUMERIC / NULLIF(portions_prepared, 0) * 100), 2) AS avg_waste_rate_pct
    FROM menu_and_waste
    GROUP BY menu_item, category
)
SELECT 
    menu_item,
    category,
    times_served,
    total_waste_kg,
    total_financial_loss,
    avg_waste_rate_pct,
    DENSE_RANK() OVER (ORDER BY total_financial_loss DESC) AS loss_rank,
    ROUND(
        total_financial_loss / SUM(total_financial_loss) OVER () * 100, 2
    ) AS pct_of_overall_mess_loss
FROM DishMetrics
ORDER BY loss_rank ASC;


-- --------------------------------------------------------------------
-- QUERY 3: Day-Over-Day (DoD) Attendance Change Using LAG()
-- Business Impact: Uncovers sudden footfall collapses (e.g. students eating out
-- on Friday/Saturday nights or exam periods).
-- --------------------------------------------------------------------
WITH DailyAttendance AS (
    SELECT 
        meal_date,
        day_name,
        meal_type,
        actual_headcount,
        LAG(actual_headcount, 1) OVER (
            PARTITION BY meal_type 
            ORDER BY meal_date
        ) AS prev_day_headcount
    FROM menu_and_waste
)
SELECT 
    meal_date,
    day_name,
    meal_type,
    actual_headcount,
    prev_day_headcount,
    (actual_headcount - prev_day_headcount) AS absolute_change,
    ROUND(
        ((actual_headcount - prev_day_headcount)::NUMERIC / NULLIF(prev_day_headcount, 0)) * 100, 2
    ) AS pct_change
FROM DailyAttendance
WHERE prev_day_headcount IS NOT NULL
ORDER BY ABS(actual_headcount - prev_day_headcount) DESC
LIMIT 15;


-- --------------------------------------------------------------------
-- QUERY 4: Meal-Skipping Cohort Analysis by Department & Academic Year
-- Business Impact: Identifies which student demographics underutilize 
-- mess meals to investigate scheduling clashes or dissatisfaction.
-- --------------------------------------------------------------------
WITH TotalMealsPossible AS (
    SELECT COUNT(DISTINCT meal_date) * 3 AS total_meals_served
    FROM menu_and_waste
),
StudentAttendanceCount AS (
    SELECT 
        s.student_id,
        s.department,
        s.year,
        s.dietary_pref,
        COUNT(a.log_id) AS meals_attended
    FROM students s
    LEFT JOIN attendance_logs a ON s.student_id = a.student_id
    GROUP BY s.student_id, s.department, s.year, s.dietary_pref
)
SELECT 
    sac.department,
    sac.year,
    COUNT(sac.student_id) AS total_students_in_cohort,
    ROUND(AVG(sac.meals_attended), 1) AS avg_meals_attended_per_student,
    ROUND(
        (AVG(sac.meals_attended)::NUMERIC / (SELECT total_meals_served FROM TotalMealsPossible)) * 100, 2
    ) AS cohort_attendance_rate_pct
FROM StudentAttendanceCount sac
GROUP BY sac.department, sac.year
ORDER BY cohort_attendance_rate_pct ASC;


-- --------------------------------------------------------------------
-- QUERY 5: Peak Dining Hall Rush Hours & Queue Congestion Percentiles
-- Business Impact: Helps administration plan staffing and open secondary 
-- counters during the top 10% longest queue windows.
-- --------------------------------------------------------------------
WITH QueueStats AS (
    SELECT 
        meal_type,
        EXTRACT(HOUR FROM check_in_time) AS check_in_hour,
        EXTRACT(MINUTE FROM check_in_time) / 15 * 15 AS interval_15min,
        COUNT(*) AS footfall_count,
        ROUND(AVG(queue_wait_minutes), 1) AS avg_wait_time_mins,
        MAX(queue_wait_minutes) AS max_wait_time_mins
    FROM attendance_logs
    GROUP BY meal_type, EXTRACT(HOUR FROM check_in_time), EXTRACT(MINUTE FROM check_in_time) / 15 * 15
)
SELECT 
    meal_type,
    CONCAT(LPAD(check_in_hour::TEXT, 2, '0'), ':', LPAD(interval_15min::TEXT, 2, '0')) AS time_window,
    footfall_count,
    avg_wait_time_mins,
    max_wait_time_mins,
    NTILE(4) OVER (PARTITION BY meal_type ORDER BY footfall_count DESC) AS congestion_quartile
FROM QueueStats
ORDER BY meal_type, footfall_count DESC;


-- --------------------------------------------------------------------
-- QUERY 6: Complaint Resolution SLA Compliance & Student Satisfaction
-- Business Impact: Audits kitchen staff responsiveness and correlates
-- unresolved complaints with student sentiment.
-- --------------------------------------------------------------------
SELECT 
    category,
    COUNT(*) AS total_complaints,
    ROUND(AVG(rating), 2) AS avg_student_rating,
    ROUND(AVG(resolution_time_hours), 1) AS avg_resolution_hours,
    ROUND(
        (COUNT(CASE WHEN resolution_time_hours <= 24 THEN 1 END)::NUMERIC / NULLIF(COUNT(CASE WHEN status = 'Resolved' THEN 1 END), 0)) * 100, 
        2
    ) AS pct_resolved_within_24hr_sla,
    COUNT(CASE WHEN status = 'Pending' THEN 1 END) AS unresolved_backlog
FROM complaints_feedback
GROUP BY category
ORDER BY total_complaints DESC;


-- --------------------------------------------------------------------
-- QUERY 7: What-If Cost Optimization (Static vs Dynamic Buffer Cooking)
-- Business Impact: Quantifies financial savings by cutting static 12% 
-- over-preparation down to dynamic 4% safety buffer.
-- --------------------------------------------------------------------
WITH WasteSimulation AS (
    SELECT 
        meal_date,
        meal_type,
        cost_per_plate_inr,
        portions_prepared AS actual_prepared,
        actual_headcount,
        -- Proposed dynamic buffer: Headcount + 4% safety margin
        CEIL(actual_headcount * 1.04) AS optimized_prepared,
        portions_wasted AS actual_portions_wasted,
        financial_loss_inr AS actual_loss_inr,
        GREATEST(0, CEIL(actual_headcount * 1.04) - actual_headcount) AS optimized_wasted_portions
    FROM menu_and_waste
)
SELECT 
    COUNT(*) AS total_meal_sessions,
    ROUND(SUM(actual_loss_inr), 2) AS total_actual_financial_loss_inr,
    ROUND(SUM(optimized_wasted_portions * cost_per_plate_inr * 0.75), 2) AS projected_optimized_loss_inr,
    ROUND(SUM(actual_loss_inr) - SUM(optimized_wasted_portions * cost_per_plate_inr * 0.75), 2) AS estimated_cost_savings_inr,
    ROUND(
        ((SUM(actual_loss_inr) - SUM(optimized_wasted_portions * cost_per_plate_inr * 0.75)) / NULLIF(SUM(actual_loss_inr), 0)) * 100,
        2
    ) AS pct_loss_reduction
FROM WasteSimulation;
