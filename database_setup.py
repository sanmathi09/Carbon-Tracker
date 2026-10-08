import sqlite3

# Connect to database
conn = sqlite3.connect("carbon_tracker.db")
cur = conn.cursor()

# -----------------------------------------------------
# TABLE 1: Users
# -----------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    city TEXT
)
""")

# -----------------------------------------------------
# TABLE 2: Categories
# -----------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT
)
""")

# -----------------------------------------------------
# TABLE 3: Activities
# -----------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS activities (
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_name TEXT,
    unit TEXT,
    emission_factor REAL
)
""")

# -----------------------------------------------------
# TABLE 4: Activity-Category Mapping
# -----------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS activity_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER,
    category_id INTEGER,
    FOREIGN KEY(activity_id) REFERENCES activities(activity_id),
    FOREIGN KEY(category_id) REFERENCES categories(category_id)
)
""")

# -----------------------------------------------------
# TABLE 5: Records (Main Table)
# -----------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    activity_id INTEGER,
    quantity REAL,
    date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(activity_id) REFERENCES activities(activity_id)
)
""")

# -----------------------------------------------------
# TABLE 6: Goals
# -----------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS goals (
    goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    target_value REAL,
    deadline TEXT,
    current_progress REAL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
""")

# -----------------------------------------------------
# TABLE 7: Carbon Summary
# -----------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS carbon_summary (
    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    total_emission REAL,
    period_type TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
""")

# -----------------------------------------------------
# TABLE 8: Feedback
# -----------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    rating INTEGER,
    comments TEXT,
    date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
""")

# -----------------------------------------------------
# INSERT DATA
# -----------------------------------------------------

# Users (10 records)
users_data = [
    ("Aarav", 21, "Bangalore"),
    ("Diya", 19, "Chennai"),
    ("Karan", 22, "Hyderabad"),
    ("Meera", 20, "Mumbai"),
    ("Riya", 23, "Delhi"),
    ("Sanjay", 25, "Pune"),
    ("Ishita", 18, "Kochi"),
    ("Rahul", 26, "Kolkata"),
    ("Neha", 20, "Chandigarh"),
    ("Vikram", 22, "Jaipur")
]
cur.executemany("INSERT INTO users (name, age, city) VALUES (?, ?, ?)", users_data)

# Categories (5)
categories_data = [
    ("Transport",),
    ("Energy",),
    ("Food",),
    ("Waste",),
    ("Household",)
]
cur.executemany("INSERT INTO categories (category_name) VALUES (?)", categories_data)

# Activities (10)
activities_data = [
    ("Car Travel (km)", "km", 0.12),
    ("Bus Travel (km)", "km", 0.03),
    ("Flight Travel (km)", "km", 0.18),
    ("Electricity Usage", "kWh", 0.82),
    ("Cooking Gas", "kg", 2.9),
    ("Food Consumption", "kg", 1.6),
    ("Plastic Waste", "kg", 1.2),
    ("Organic Waste", "kg", 0.3),
    ("AC Usage", "hours", 1.0),
    ("Water Usage", "liters", 0.002)
]
cur.executemany("INSERT INTO activities (activity_name, unit, emission_factor) VALUES (?, ?, ?)", activities_data)

# Activity-Category Mapping (10)
activity_category_data = [
    (1,1), (2,1), (3,1),   # Transport
    (4,2), (9,2),          # Energy
    (5,5), (10,5),         # Household
    (6,3),                 # Food
    (7,4), (8,4)           # Waste
]
cur.executemany("INSERT INTO activity_category (activity_id, category_id) VALUES (?, ?)", activity_category_data)

# Records (40 entries)
records_data = [
    (1,1,12,"2024-01-01"),
    (1,4,5,"2024-01-02"),
    (2,2,20,"2024-01-03"),
    (2,5,1,"2024-01-04"),
    (3,1,25,"2024-01-05"),
    (3,7,2,"2024-01-06"),
    (4,2,15,"2024-01-07"),
    (4,4,10,"2024-01-08"),
    (5,3,50,"2024-01-09"),
    (5,6,4,"2024-01-10"),
    (6,1,18,"2024-01-11"),
    (6,10,40,"2024-01-12"),
    (7,4,12,"2024-01-13"),
    (7,8,3,"2024-01-14"),
    (8,5,2,"2024-01-15"),
    (8,7,3,"2024-01-16"),
    (9,6,3,"2024-01-17"),
    (9,1,9,"2024-01-18"),
    (10,9,6,"2024-01-19"),
    (10,3,30,"2024-01-20"),
    (1,2,10,"2024-01-21"),
    (2,1,14,"2024-01-22"),
    (3,4,11,"2024-01-23"),
    (4,7,3,"2024-01-24"),
    (5,10,100,"2024-01-25"),
    (6,6,2,"2024-01-26"),
    (7,2,40,"2024-01-27"),
    (8,1,22,"2024-01-28"),
    (9,5,1,"2024-01-29"),
    (10,8,2,"2024-01-30"),
    (3,10,70,"2024-01-31"),
    (4,4,9,"2024-02-01"),
    (5,7,2,"2024-02-02"),
    (9,3,25,"2024-02-03"),
    (6,9,5,"2024-02-04"),
    (8,2,24,"2024-02-05"),
    (7,6,1,"2024-02-06"),
    (10,1,15,"2024-02-07"),
    (2,10,85,"2024-02-08")
]
cur.executemany("INSERT INTO records (user_id, activity_id, quantity, date) VALUES (?, ?, ?, ?)", records_data)

# Commit & Close
conn.commit()
conn.close()

print("Database with 8 tables and 40+ records created successfully!")
