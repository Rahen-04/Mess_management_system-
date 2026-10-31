"""
Mess Operations & Demand Analytics - Synthetic Data Generator
Generates ~60,000+ realistic relational records spanning 180 days of university mess operations.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. Generate Students (500 students across 4 batches & 5 branches)
# -------------------------------------------------------------
departments = ['Computer Science', 'Electrical Eng', 'Mechanical Eng', 'Civil Eng', 'Chemical Eng']
dept_codes = {'Computer Science': 'CS', 'Electrical Eng': 'EE', 'Mechanical Eng': 'ME', 'Civil Eng': 'CE', 'Chemical Eng': 'CH'}
years = ['1st Year', '2nd Year', '3rd Year', '4th Year']
year_prefixes = {'1st Year': '2301', '2nd Year': '2201', '3rd Year': '2101', '4th Year': '2001'}
diet_options = ['Vegetarian', 'Non-Vegetarian']

students = []
student_id_counter = 1

for year in years:
    prefix = year_prefixes[year]
    for dept in departments:
        code = dept_codes[dept]
        for i in range(1, 26):  # 25 students per branch per year = 500 total
            sid = f"{prefix}{code}{i:02d}"
            diet = np.random.choice(diet_options, p=[0.45, 0.55])
            students.append({
                'student_id': sid,
                'department': dept,
                'year': year,
                'dietary_pref': diet,
                'hostel_block': np.random.choice(['Block A (Boys)', 'Block B (Boys)', 'Block C (Girls)'], p=[0.4, 0.4, 0.2]),
                'registered_date': '2023-08-15'
            })

df_students = pd.DataFrame(students)
df_students.to_csv(os.path.join(DATA_DIR, 'students.csv'), index=False)
print(f"Generated {len(df_students)} student records -> students.csv")

# -------------------------------------------------------------
# 2. Daily Menus, Food Waste & Financial Loss (180 days x 3 meals)
# -------------------------------------------------------------
start_date = datetime(2023, 9, 1)
total_days = 180

menus = {
    'Breakfast': [
        ('Idli Vada Sambar', 'South Indian', 32),
        ('Aloo Paratha & Curd', 'North Indian', 38),
        ('Poha & Boiled Eggs/Sprouts', 'Light Indian', 30),
        ('Masala Dosa & Chutney', 'South Indian', 36),
        ('Puri Sabzi', 'North Indian', 34),
        ('Bread Omelette / Veg Sandwich', 'Continental', 35),
        ('Chole Bhature (Weekend Special)', 'North Indian', 42)
    ],
    'Lunch': [
        ('Dal Makhani, Rice, Roti, Salad', 'North Indian', 55),
        ('Rajma Masala, Jeera Rice, Mixed Veg', 'North Indian', 52),
        ('Paneer Butter Masala / Chicken Curry', 'Special Lunch', 68),
        ('Sambhar Rice, Poriyal, Curd Rice', 'South Indian', 48),
        ('Chole Kulche, Raita, Pulao', 'North Indian', 56),
        ('Kadhi Pakora, Steamed Rice, Aloo Bhindi', 'Comfort Food', 50),
        ('Egg Biryani / Veg Dum Biryani', 'Biryani Special', 65)
    ],
    'Dinner': [
        ('Shahi Paneer / Butter Chicken, Naan', 'North Indian Deluxe', 75),
        ('Yellow Dal Tadka, Seasonal Sabzi, Phulka', 'Light Dinner', 45),
        ('Veg Pulao, Paneer Do Pyaza, Gulab Jamun', 'Feast Dinner', 70),
        ('Hyderabadi Chicken/Veg Biryani & Mirchi Salan', 'Sunday Special', 80),
        ('Mix Veg Curry, Dal Fry, Roti, Kheer', 'Deluxe Dinner', 62),
        ('Khichdi, Papad, Aloo Chokha, Dahi', 'Light Dinner', 40),
        ('Pav Bhaji, Tawa Pulao, Ice Cream', 'Weekend Treat', 65)
    ]
}

# Special periods
mid_term_exam = (datetime(2023, 10, 15), datetime(2023, 10, 23))
end_term_exam = (datetime(2023, 12, 1), datetime(2023, 12, 12))
diwali_break = (datetime(2023, 11, 10), datetime(2023, 11, 15))

meal_events = []
attendance_logs = []
complaints = []
log_id = 1
complaint_id = 1

student_ids = df_students['student_id'].tolist()
total_students = len(student_ids)

for day_idx in range(total_days):
    current_date = start_date + timedelta(days=day_idx)
    date_str = current_date.strftime('%Y-%m-%d')
    is_weekend = current_date.weekday() >= 5
    is_sunday = current_date.weekday() == 6
    is_midsem = mid_term_exam[0] <= current_date <= mid_term_exam[1]
    is_endsem = end_term_exam[0] <= current_date <= end_term_exam[1]
    is_diwali = diwali_break[0] <= current_date <= diwali_break[1]

    # Effective student population on campus (drops during vacation)
    effective_pop_ratio = 0.35 if is_diwali else 1.0

    for meal_type in ['Breakfast', 'Lunch', 'Dinner']:
        # Select menu item based on day
        if is_weekend and meal_type == 'Breakfast':
            menu_item, category, cost_plate = menus['Breakfast'][6]  # Chole Bhature
        elif is_sunday and meal_type == 'Dinner':
            menu_item, category, cost_plate = menus['Dinner'][3]  # Sunday Biryani Special
        else:
            menu_idx = (day_idx + (0 if meal_type=='Breakfast' else 1 if meal_type=='Lunch' else 2)) % len(menus[meal_type])
            menu_item, category, cost_plate = menus[meal_type][menu_idx]

        # Calculate base attendance probability
        if meal_type == 'Breakfast':
            base_prob = 0.62
            if is_weekend: base_prob -= 0.22  # Students sleep late
            if is_midsem or is_endsem: base_prob -= 0.15  # Late night studies, skip morning
        elif meal_type == 'Lunch':
            base_prob = 0.78
            if is_weekend: base_prob -= 0.10
        else:  # Dinner
            base_prob = 0.88
            if is_sunday: base_prob += 0.08  # Everyone shows up for Sunday special
            if is_midsem or is_endsem: base_prob += 0.04  # In hostel studying

        # Menu quality modifier
        if 'Biryani' in menu_item or 'Butter' in menu_item or 'Bhature' in menu_item:
            base_prob += 0.06
        elif 'Khichdi' in menu_item or 'Light' in category:
            base_prob -= 0.08

        base_prob = max(0.15, min(0.96, base_prob * effective_pop_ratio))

        # Sample attending students
        attending_mask = np.random.rand(total_students) < base_prob
        attending_students = [student_ids[i] for i in range(total_students) if attending_mask[i]]
        headcount = len(attending_students)

        # Buffer cooked: Mess cooks for ~5-15% above estimated average
        estimated_planning = int(total_students * (0.65 if meal_type=='Breakfast' else 0.80 if meal_type=='Lunch' else 0.88) * effective_pop_ratio)
        portions_prepared = int(estimated_planning * np.random.uniform(1.02, 1.12))
        portions_consumed = min(portions_prepared, headcount)
        portions_wasted = max(0, portions_prepared - portions_consumed)

        # Waste calculations
        kg_per_portion = 0.35 if meal_type == 'Breakfast' else 0.50
        food_wasted_kg = round(portions_wasted * kg_per_portion, 2)
        financial_loss_inr = round(portions_wasted * cost_plate * 0.75, 2)  # Raw ingredient cost factor ~75%

        meal_events.append({
            'meal_date': date_str,
            'day_name': current_date.strftime('%A'),
            'meal_type': meal_type,
            'menu_item': menu_item,
            'category': category,
            'cost_per_plate_inr': cost_plate,
            'portions_prepared': portions_prepared,
            'actual_headcount': headcount,
            'portions_wasted': portions_wasted,
            'food_wasted_kg': food_wasted_kg,
            'financial_loss_inr': financial_loss_inr
        })

        # Generate attendance check-in logs with realistic timing & queue wait
        if meal_type == 'Breakfast':
            base_hour, window_mins = 8, 120
        elif meal_type == 'Lunch':
            base_hour, window_mins = 12, 120
        else:
            base_hour, window_mins = 19, 135

        for student_id in attending_students:
            # Distribution peaks in middle of meal window
            minute_offset = int(np.random.beta(2, 2) * window_mins)
            check_in_dt = current_date.replace(hour=base_hour, minute=0, second=0) + timedelta(minutes=minute_offset)
            
            # Queue delay is highest during peak 30 mins
            if 30 <= minute_offset <= 75:
                queue_wait = int(np.random.normal(8, 2.5))
            else:
                queue_wait = int(np.random.normal(3, 1.2))
            queue_wait = max(1, queue_wait)

            attendance_logs.append({
                'log_id': log_id,
                'student_id': student_id,
                'meal_date': date_str,
                'meal_type': meal_type,
                'check_in_time': check_in_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'queue_wait_minutes': queue_wait,
                'scan_status': 'Verified'
            })
            log_id += 1

        # Occasional complaints / feedback (approx 1-3 complaints per meal)
        if np.random.rand() < 0.65 and headcount > 0:
            num_complaints = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
            for _ in range(num_complaints):
                complaining_student = np.random.choice(attending_students)
                cat = np.random.choice(['Food Quality', 'Hygiene & Cleanliness', 'Shortage/Quantity', 'Delay/Long Queues', 'Staff Behavior'],
                                       p=[0.35, 0.25, 0.15, 0.15, 0.10])
                
                # Rating correlated with complaint category
                if cat == 'Food Quality':
                    rating = np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
                    text = np.random.choice([
                        f"Roti was cold and hard during {meal_type.lower()}.",
                        f"Excess oil and salt in {menu_item}.",
                        f"Food lacked proper taste and seasoning.",
                        f"Dal was too watery today."
                    ])
                elif cat == 'Hygiene & Cleanliness':
                    rating = np.random.choice([1, 2], p=[0.6, 0.4])
                    text = np.random.choice([
                        "Water dispenser glasses were unwashed.",
                        "Dining tables were not wiped down properly.",
                        "Found hair in food tray.",
                        "Handwash station liquid soap was empty."
                    ])
                elif cat == 'Shortage/Quantity':
                    rating = np.random.choice([1, 2], p=[0.5, 0.5])
                    text = f"Main curry ran out 30 minutes before {meal_type.lower()} end time."
                elif cat == 'Delay/Long Queues':
                    rating = np.random.choice([2, 3], p=[0.6, 0.4])
                    text = "Single counter open during peak rush. Queue took over 15 minutes."
                else:
                    rating = np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
                    text = "Catering staff was rude when asked for refill."

                # Status and SLA resolution time
                status = np.random.choice(['Resolved', 'In Progress', 'Pending'], p=[0.75, 0.15, 0.10])
                res_time = round(np.random.exponential(18) + 2, 1) if status == 'Resolved' else None

                complaints.append({
                    'complaint_id': complaint_id,
                    'student_id': complaining_student,
                    'submission_date': date_str,
                    'meal_type': meal_type,
                    'category': cat,
                    'rating': rating,
                    'feedback_text': text,
                    'status': status,
                    'resolution_time_hours': res_time
                })
                complaint_id += 1

# Export datasets
df_meals = pd.DataFrame(meal_events)
df_meals.to_csv(os.path.join(DATA_DIR, 'menu_and_waste.csv'), index=False)
print(f"Generated {len(df_meals)} meal event records -> menu_and_waste.csv")

df_attendance = pd.DataFrame(attendance_logs)
df_attendance.to_csv(os.path.join(DATA_DIR, 'attendance_logs.csv'), index=False)
print(f"Generated {len(df_attendance)} attendance check-in records -> attendance_logs.csv")

df_complaints = pd.DataFrame(complaints)
df_complaints.to_csv(os.path.join(DATA_DIR, 'complaints_feedback.csv'), index=False)
print(f"Generated {len(df_complaints)} feedback & complaint records -> complaints_feedback.csv")

print("\n--- Data Generation Completed Successfully! ---")
