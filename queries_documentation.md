# Database Queries Documentation

This document lists the 10+ database queries used in the Carbon Footprint Activity Tracker application:

## 1. View All Records (with JOIN)
```sql
SELECT r.record_id, u.name, a.activity_name, r.quantity, r.date,
       ROUND(r.quantity * a.emission_factor, 2) as emission
FROM records r
JOIN users u ON r.user_id = u.user_id
JOIN activities a ON r.activity_id = a.activity_id
ORDER BY r.record_id ASC
```

## 2. Get Users for Dropdown
```sql
SELECT user_id, name FROM users
```

## 3. Get Activities for Dropdown
```sql
SELECT activity_id, activity_name, unit FROM activities
```

## 4. Insert New Record
```sql
INSERT INTO records (user_id, activity_id, quantity, date) VALUES (?, ?, ?, ?)
```

## 5. Emissions by User (for Charts)
```sql
SELECT u.name, SUM(r.quantity * a.emission_factor) as total_emission
FROM records r
JOIN users u ON r.user_id = u.user_id
JOIN activities a ON r.activity_id = a.activity_id
GROUP BY u.name
ORDER BY total_emission DESC
```

## 6. Emissions by Activity (for Charts)
```sql
SELECT a.activity_name, SUM(r.quantity * a.emission_factor) as total_emission
FROM records r
JOIN activities a ON r.activity_id = a.activity_id
GROUP BY a.activity_name
ORDER BY total_emission DESC
```

## 7. Summary by User (for PDF Report)
```sql
SELECT u.name, COUNT(r.record_id) as total_records,
       SUM(r.quantity * a.emission_factor) as total_emission
FROM records r
JOIN users u ON r.user_id = u.user_id
JOIN activities a ON r.activity_id = a.activity_id
GROUP BY u.name
ORDER BY total_emission DESC
```

## 8. Recent Records (for PDF Report)
```sql
SELECT r.record_id, u.name, a.activity_name, r.quantity, r.date,
       ROUND(r.quantity * a.emission_factor, 2) as emission
FROM records r
JOIN users u ON r.user_id = u.user_id
JOIN activities a ON r.activity_id = a.activity_id
ORDER BY r.date DESC
LIMIT 20
```

## 9. All Records for Excel Export
```sql
SELECT r.record_id, u.name as user_name, a.activity_name, 
       r.quantity, r.date, a.unit,
       ROUND(r.quantity * a.emission_factor, 2) as emission_kg_co2
FROM records r
JOIN users u ON r.user_id = u.user_id
JOIN activities a ON r.activity_id = a.activity_id
ORDER BY r.date
```

## 10. Summary for Excel Export
```sql
SELECT u.name, COUNT(r.record_id) as total_records,
       SUM(r.quantity * a.emission_factor) as total_emission_kg_co2
FROM records r
JOIN users u ON r.user_id = u.user_id
JOIN activities a ON r.activity_id = a.activity_id
GROUP BY u.name
ORDER BY total_emission_kg_co2 DESC
```

## Database Structure
- **8 Tables**: users, categories, activities, activity_category, records, goals, carbon_summary, feedback
- **39+ Records**: Pre-populated with sample data
- **Multiple JOINs**: Complex queries using multiple table relationships
- **Aggregations**: SUM, COUNT, GROUP BY operations
- **Calculations**: Real-time CO2 emission calculations using emission factors