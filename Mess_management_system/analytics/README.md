# 📊 Mess Operations & Demand Analytics Suite

This directory contains the complete data engineering, SQL analytics, Python EDA, and executive dashboard suite for the Mess Management System.

---

## 📁 Directory Structure

```text
analytics/
├── data/
│   ├── raw/                  # 195,000+ generated CSV records
│   │   ├── students.csv
│   │   ├── menu_and_waste.csv
│   │   ├── attendance_logs.csv
│   │   └── complaints_feedback.csv
│   └── processed/
│       ├── summary_metrics.json          # Precomputed metrics for dashboards
│       └── mess_operations_dataset.xlsx  # Multi-tab workbook for Power BI / Tableau / Excel
├── scripts/
│   ├── data_generator.py     # Generates 180 days of realistic relational logs
│   └── eda_analysis.py       # Python statistical aggregations & chart exports
├── sql/
│   ├── schema.sql            # PostgreSQL table definitions & analytical indexes
│   └── queries.sql           # Production-grade SQL queries (CTEs, Window functions)
├── visuals/                  # High-resolution PNG charts (300 DPI)
│   ├── 1_attendance_by_meal_and_day.png
│   ├── 2_food_waste_and_loss_by_category.png
│   ├── 3_exam_period_attendance_trend.png
│   ├── 4_complaint_categories_and_sla.png
│   └── 5_queue_wait_distribution.png
├── dashboard/
│   └── index.html            # Interactive executive dashboard (Chart.js + Tailwind)
├── CASE_STUDY.md             # In-depth executive case study & business recommendations
└── README.md
```

---

## 🚀 Quickstart & Usage

### 1. View the Interactive Dashboard
Simply double-click [`dashboard/index.html`](dashboard/index.html) to open it in any web browser. No web server or setup required!

### 2. Run the Analytics Pipeline
To regenerate the datasets or modify parameters:
```bash
# 1. Generate 180-day operational dataset (195k+ records)
python scripts/data_generator.py

# 2. Run Python Exploratory Data Analysis & export charts + Excel
python scripts/eda_analysis.py
```

### 3. Run the SQL Queries in PostgreSQL
Import [`sql/schema.sql`](sql/schema.sql) into PostgreSQL:
```sql
\i sql/schema.sql
```
Then execute any of the 7 business scenario queries in [`sql/queries.sql`](sql/queries.sql).

### 4. Power BI / Tableau Integration
Open [`data/processed/mess_operations_dataset.xlsx`](data/processed/mess_operations_dataset.xlsx) in Power BI Desktop or Tableau to build additional dashboards using pre-cleaned dimensional tables:
* `Daily Meals & Waste`
* `Waste by Category`
* `Complaints & SLA`
* `Students Cohort`
