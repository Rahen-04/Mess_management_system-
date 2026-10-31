-- ====================================================================
-- Mess Operations & Demand Analytics - PostgreSQL Database Schema
-- ====================================================================

-- 1. Students Entity
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(20) PRIMARY KEY,
    department VARCHAR(50) NOT NULL,
    year VARCHAR(20) NOT NULL,
    dietary_pref VARCHAR(20) NOT NULL,
    hostel_block VARCHAR(50) NOT NULL,
    registered_date DATE NOT NULL
);

-- 2. Daily Menus & Food Waste Entity
CREATE TABLE IF NOT EXISTS menu_and_waste (
    meal_date DATE NOT NULL,
    day_name VARCHAR(15) NOT NULL,
    meal_type VARCHAR(20) NOT NULL,
    menu_item VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    cost_per_plate_inr NUMERIC(6, 2) NOT NULL,
    portions_prepared INT NOT NULL,
    actual_headcount INT NOT NULL,
    portions_wasted INT NOT NULL,
    food_wasted_kg NUMERIC(6, 2) NOT NULL,
    financial_loss_inr NUMERIC(8, 2) NOT NULL,
    PRIMARY KEY (meal_date, meal_type)
);

-- 3. Attendance Check-in Logs (High Volume Transactional Table)
CREATE TABLE IF NOT EXISTS attendance_logs (
    log_id BIGSERIAL PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    meal_date DATE NOT NULL,
    meal_type VARCHAR(20) NOT NULL,
    check_in_time TIMESTAMP NOT NULL,
    queue_wait_minutes INT NOT NULL,
    scan_status VARCHAR(20) DEFAULT 'Verified'
);

-- 4. Complaints & Feedback Entity
CREATE TABLE IF NOT EXISTS complaints_feedback (
    complaint_id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    submission_date DATE NOT NULL,
    meal_type VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    resolution_time_hours NUMERIC(5, 1)
);

-- ====================================================================
-- Performance Indexes for High-Concurrency & Analytical Queries
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_attendance_date_meal ON attendance_logs(meal_date, meal_type);
CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance_logs(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_checkin ON attendance_logs(check_in_time);
CREATE INDEX IF NOT EXISTS idx_menu_date ON menu_and_waste(meal_date);
CREATE INDEX IF NOT EXISTS idx_complaints_category_status ON complaints_feedback(category, status);
