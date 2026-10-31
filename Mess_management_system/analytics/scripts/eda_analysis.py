"""
Mess Operations & Demand Analytics - Python Exploratory Data Analysis (EDA)
Performs statistical analysis, time-series aggregation, and generates high-res visualization charts.
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Styling configurations for publication-ready aesthetics
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
VISUALS_DIR = os.path.join(BASE_DIR, 'visuals')

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(VISUALS_DIR, exist_ok=True)

print("Loading raw datasets...")
df_students = pd.read_csv(os.path.join(RAW_DIR, 'students.csv'))
df_meals = pd.read_csv(os.path.join(RAW_DIR, 'menu_and_waste.csv'))
df_attendance = pd.read_csv(os.path.join(RAW_DIR, 'attendance_logs.csv'))
df_complaints = pd.read_csv(os.path.join(RAW_DIR, 'complaints_feedback.csv'))

df_meals['meal_date'] = pd.to_datetime(df_meals['meal_date'])
df_attendance['check_in_time'] = pd.to_datetime(df_attendance['check_in_time'])
df_complaints['submission_date'] = pd.to_datetime(df_complaints['submission_date'])

# -------------------------------------------------------------
# CHART 1: Attendance Distribution by Day of Week & Meal Type
# -------------------------------------------------------------
print("Generating Chart 1: Attendance by Day and Meal Type...")
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
attendance_day = df_meals.groupby(['day_name', 'meal_type'])['actual_headcount'].mean().unstack()[['Breakfast', 'Lunch', 'Dinner']].reindex(day_order)

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
colors = ['#f59e0b', '#3b82f6', '#10b981']
attendance_day.plot(kind='bar', ax=ax, color=colors, width=0.8, edgecolor='none')

ax.set_title("Average Meal Headcount by Day of Week", pad=15, fontweight='bold', color='#1e293b')
ax.set_ylabel("Average Students in Attendance", fontweight='semibold')
ax.set_xlabel("Day of Week", fontweight='semibold')
ax.set_xticklabels(day_order, rotation=0)
ax.legend(title="Meal Type", frameon=True, facecolor='#ffffff')
ax.set_ylim(0, 520)

# Add reference line for total registered students
ax.axhline(500, color='#ef4444', linestyle='--', linewidth=1.2, label='Total Capacity (500)')
ax.legend()
plt.tight_layout()
fig.savefig(os.path.join(VISUALS_DIR, '1_attendance_by_meal_and_day.png'))
plt.close(fig)

# -------------------------------------------------------------
# CHART 2: Food Waste (kg) and Financial Loss by Category
# -------------------------------------------------------------
print("Generating Chart 2: Food Waste & Financial Loss by Category...")
cat_waste = df_meals.groupby('category').agg({
    'food_wasted_kg': 'sum',
    'financial_loss_inr': 'sum',
    'actual_headcount': 'count'
}).rename(columns={'actual_headcount': 'times_served'}).sort_values(by='financial_loss_inr', ascending=False)

fig, ax1 = plt.subplots(figsize=(11, 5.5), dpi=300)
color1 = '#6366f1'
color2 = '#ef4444'

x = np.arange(len(cat_waste))
width = 0.38

rects1 = ax1.bar(x - width/2, cat_waste['food_wasted_kg'], width, label='Total Waste (kg)', color=color1)
ax1.set_ylabel('Total Food Wasted (kg)', color=color1, fontweight='semibold')
ax1.set_xticks(x)
ax1.set_xticklabels(cat_waste.index, rotation=25, ha='right')
ax1.tick_params(axis='y', labelcolor=color1)

ax2 = ax1.twinx()
rects2 = ax2.bar(x + width/2, cat_waste['financial_loss_inr'], width, label='Financial Loss (₹)', color=color2)
ax2.set_ylabel('Total Financial Loss (₹)', color=color2, fontweight='semibold')
ax2.tick_params(axis='y', labelcolor=color2)

plt.title("Total Food Waste (kg) and Financial Loss (₹) by Cuisine / Menu Category", pad=15, fontweight='bold', color='#1e293b')
ax1.grid(False)
ax2.grid(False)
plt.tight_layout()
fig.savefig(os.path.join(VISUALS_DIR, '2_food_waste_and_loss_by_category.png'))
plt.close(fig)

# -------------------------------------------------------------
# CHART 3: 7-Day Moving Average Attendance & Exam Dips
# -------------------------------------------------------------
print("Generating Chart 3: 7-Day Moving Average & Trends...")
daily_total = df_meals.groupby(['meal_date', 'meal_type'])['actual_headcount'].sum().unstack()
daily_rolling = daily_total.rolling(window=7, min_periods=1).mean()

fig, ax = plt.subplots(figsize=(12, 5.5), dpi=300)
ax.plot(daily_rolling.index, daily_rolling['Breakfast'], label='Breakfast (7-Day Rolling)', color='#f59e0b', linewidth=2)
ax.plot(daily_rolling.index, daily_rolling['Lunch'], label='Lunch (7-Day Rolling)', color='#3b82f6', linewidth=2)
ax.plot(daily_rolling.index, daily_rolling['Dinner'], label='Dinner (7-Day Rolling)', color='#10b981', linewidth=2)

# Highlight Exam and Holiday Windows
ax.axvspan(pd.to_datetime('2023-10-15'), pd.to_datetime('2023-10-23'), color='#f87171', alpha=0.25, label='Mid-Term Exams')
ax.axvspan(pd.to_datetime('2023-11-10'), pd.to_datetime('2023-11-15'), color='#fbbf24', alpha=0.25, label='Diwali Vacation')
ax.axvspan(pd.to_datetime('2023-12-01'), pd.to_datetime('2023-12-12'), color='#f87171', alpha=0.35, label='End-Term Exams')

ax.set_title("180-Day Trend: Meal Footfall & Impact of Exam / Vacation Periods", pad=15, fontweight='bold', color='#1e293b')
ax.set_ylabel("Rolling 7-Day Average Headcount", fontweight='semibold')
ax.set_xlabel("Date", fontweight='semibold')
ax.legend(loc='lower left', frameon=True, facecolor='#ffffff')
plt.tight_layout()
fig.savefig(os.path.join(VISUALS_DIR, '3_exam_period_attendance_trend.png'))
plt.close(fig)

# -------------------------------------------------------------
# CHART 4: Complaints Breakdown and SLA Resolution Time
# -------------------------------------------------------------
print("Generating Chart 4: Complaints & SLA Analysis...")
complaint_summary = df_complaints.groupby('category').agg({
    'complaint_id': 'count',
    'rating': 'mean',
    'resolution_time_hours': 'mean'
}).rename(columns={'complaint_id': 'count'}).sort_values(by='count', ascending=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

# Horizontal bar of complaint volume
ax1.barh(complaint_summary.index, complaint_summary['count'], color='#38bdf8', edgecolor='none')
ax1.set_title("Complaint Volume by Category", pad=12, fontweight='bold', color='#1e293b')
ax1.set_xlabel("Number of Complaints")

# Resolution SLA
ax2.barh(complaint_summary.index, complaint_summary['resolution_time_hours'], color='#fb7185', edgecolor='none')
ax2.axvline(24, color='#dc2626', linestyle='--', label='24hr SLA Target')
ax2.set_title("Avg Administrative Resolution Time (Hours)", pad=12, fontweight='bold', color='#1e293b')
ax2.set_xlabel("Hours to Resolve")
ax2.legend()

plt.tight_layout()
fig.savefig(os.path.join(VISUALS_DIR, '4_complaint_categories_and_sla.png'))
plt.close(fig)

# -------------------------------------------------------------
# CHART 5: Queue Delay & Footfall Arrival Distribution
# -------------------------------------------------------------
print("Generating Chart 5: Queue Wait Times...")
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
sns.kdeplot(data=df_attendance, x='queue_wait_minutes', hue='meal_type', common_norm=False, fill=True, alpha=0.3, palette=['#f59e0b', '#3b82f6', '#10b981'], ax=ax)
ax.set_title("Queue Wait Time Probability Distribution by Meal", pad=15, fontweight='bold', color='#1e293b')
ax.set_xlabel("Queue Wait Time (Minutes)")
ax.set_ylabel("Density")
plt.tight_layout()
fig.savefig(os.path.join(VISUALS_DIR, '5_queue_wait_distribution.png'))
plt.close(fig)

# -------------------------------------------------------------
# 5. Export Key Metrics & Excel Report for Dashboard & Power BI
# -------------------------------------------------------------
print("Exporting processed metrics and Excel workbook...")

total_meals_served = int(df_meals['actual_headcount'].sum())
total_food_waste_kg = float(round(df_meals['food_wasted_kg'].sum(), 1))
total_financial_loss_inr = float(round(df_meals['financial_loss_inr'].sum(), 2))
avg_daily_attendance = float(round(df_meals.groupby('meal_date')['actual_headcount'].sum().mean(), 1))
avg_complaint_rating = float(round(df_complaints['rating'].mean(), 2))
sla_resolution_rate = float(round((df_complaints['status'] == 'Resolved').mean() * 100, 1))

# Dynamic buffer optimization savings estimation
actual_portions_wasted = int(df_meals['portions_wasted'].sum())
optimized_waste = df_meals.apply(lambda r: max(0, int(np.ceil(r['actual_headcount'] * 1.04)) - r['actual_headcount']), axis=1)
optimized_loss = float(round((optimized_waste * df_meals['cost_per_plate_inr'] * 0.75).sum(), 2))
potential_savings_inr = float(round(total_financial_loss_inr - optimized_loss, 2))
pct_loss_reduction = float(round((potential_savings_inr / total_financial_loss_inr) * 100, 1))

summary_data = {
    'total_registered_students': len(df_students),
    'total_days_analyzed': 180,
    'total_meals_served': total_meals_served,
    'avg_daily_attendance': avg_daily_attendance,
    'total_food_waste_kg': total_food_waste_kg,
    'total_financial_loss_inr': total_financial_loss_inr,
    'projected_savings_inr': potential_savings_inr,
    'pct_waste_reduction': pct_loss_reduction,
    'total_complaints': len(df_complaints),
    'avg_student_rating': avg_complaint_rating,
    'sla_resolved_pct': sla_resolution_rate,
    'top_waste_categories': cat_waste[['food_wasted_kg', 'financial_loss_inr']].head(5).to_dict(orient='index'),
    'day_of_week_attendance': attendance_day.to_dict(orient='index')
}

with open(os.path.join(PROCESSED_DIR, 'summary_metrics.json'), 'w') as f:
    json.dump(summary_data, f, indent=4)

# Create an Excel workbook with multiple tabs for Power BI / Excel portfolios
excel_path = os.path.join(PROCESSED_DIR, 'mess_operations_dataset.xlsx')
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df_meals.to_excel(writer, sheet_name='Daily Meals & Waste', index=False)
    cat_waste.reset_index().to_excel(writer, sheet_name='Waste by Category', index=False)
    df_complaints.to_excel(writer, sheet_name='Complaints & SLA', index=False)
    df_students.to_excel(writer, sheet_name='Students Cohort', index=False)

print(f"Excel report saved: {excel_path}")
print(f"Summary metrics saved: {os.path.join(PROCESSED_DIR, 'summary_metrics.json')}")
print("--- EDA Analysis Complete! All visuals exported. ---")
