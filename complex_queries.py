"""
Complex SQL Queries for Carbon Footprint Tracker
Contains 10 advanced queries with subqueries, window functions, and complex aggregations
"""

import sqlite3
from datetime import datetime

class ComplexQueries:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.cursor = db_connection.cursor()
    
    def query_1_user_ranking_with_percentiles(self):
        """Query 1: User ranking with percentile calculations using window functions"""
        return self.cursor.execute("""
            WITH user_emissions AS (
                SELECT u.name, 
                       SUM(r.quantity * a.emission_factor) as total_emissions,
                       COUNT(r.record_id) as activity_count
                FROM users u
                JOIN records r ON u.user_id = r.user_id
                JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY u.user_id, u.name
            )
            SELECT name, total_emissions, activity_count,
                   RANK() OVER (ORDER BY total_emissions DESC) as emission_rank,
                   NTILE(4) OVER (ORDER BY total_emissions) as quartile,
                   PERCENT_RANK() OVER (ORDER BY total_emissions) * 100 as percentile
            FROM user_emissions
            ORDER BY total_emissions DESC
        """).fetchall()
    
    def query_2_monthly_growth_analysis(self):
        """Query 2: Monthly emission growth with lag functions and percentage change"""
        return self.cursor.execute("""
            WITH monthly_data AS (
                SELECT strftime('%Y-%m', r.date) as month,
                       SUM(r.quantity * a.emission_factor) as monthly_emissions
                FROM records r
                JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY strftime('%Y-%m', r.date)
            )
            SELECT month, monthly_emissions,
                   LAG(monthly_emissions) OVER (ORDER BY month) as prev_month,
                   monthly_emissions - LAG(monthly_emissions) OVER (ORDER BY month) as change,
                   ROUND(((monthly_emissions - LAG(monthly_emissions) OVER (ORDER BY month)) / 
                          LAG(monthly_emissions) OVER (ORDER BY month)) * 100, 2) as pct_change,
                   AVG(monthly_emissions) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_avg
            FROM monthly_data
            ORDER BY month
        """).fetchall()
    
    def query_3_activity_correlation_matrix(self):
        """Query 3: Activity correlation with complex subqueries and statistical analysis"""
        return self.cursor.execute("""
            SELECT a1.activity_name as activity1, a2.activity_name as activity2,
                   COUNT(*) as co_occurrence,
                   AVG(r1.quantity * a1.emission_factor) as avg_emission1,
                   AVG(r2.quantity * a2.emission_factor) as avg_emission2,
                   (SELECT AVG(total_user_emission) FROM (
                       SELECT SUM(r.quantity * a.emission_factor) as total_user_emission
                       FROM records r 
                       JOIN activities a ON r.activity_id = a.activity_id
                       WHERE r.user_id IN (
                           SELECT DISTINCT r1.user_id FROM records r1 
                           WHERE r1.activity_id = a1.activity_id
                           INTERSECT
                           SELECT DISTINCT r2.user_id FROM records r2 
                           WHERE r2.activity_id = a2.activity_id
                       )
                       GROUP BY r.user_id
                   )) as avg_combined_user_emission
            FROM activities a1
            JOIN activities a2 ON a1.activity_id < a2.activity_id
            JOIN records r1 ON a1.activity_id = r1.activity_id
            JOIN records r2 ON a2.activity_id = r2.activity_id AND r1.user_id = r2.user_id
            GROUP BY a1.activity_id, a2.activity_id, a1.activity_name, a2.activity_name
            HAVING COUNT(*) > 1
            ORDER BY co_occurrence DESC
        """).fetchall()
    
    def query_4_top_contributors_by_category(self):
        """Query 4: Top contributors by activity category with recursive CTEs"""
        return self.cursor.execute("""
            WITH RECURSIVE activity_categories AS (
                SELECT activity_name,
                       CASE 
                           WHEN activity_name LIKE '%travel%' OR activity_name LIKE '%car%' 
                                OR activity_name LIKE '%flight%' OR activity_name LIKE '%bus%' THEN 'Transportation'
                           WHEN activity_name LIKE '%electric%' OR activity_name LIKE '%energy%' 
                                OR activity_name LIKE '%power%' THEN 'Energy'
                           WHEN activity_name LIKE '%food%' OR activity_name LIKE '%meal%' 
                                OR activity_name LIKE '%meat%' THEN 'Food'
                           WHEN activity_name LIKE '%waste%' OR activity_name LIKE '%plastic%' THEN 'Waste'
                           ELSE 'Other'
                       END as category,
                       activity_id
                FROM activities
            ),
            category_totals AS (
                SELECT ac.category,
                       SUM(r.quantity * a.emission_factor) as category_total,
                       COUNT(DISTINCT r.user_id) as user_count,
                       COUNT(r.record_id) as record_count
                FROM activity_categories ac
                JOIN activities a ON ac.activity_id = a.activity_id
                JOIN records r ON a.activity_id = r.activity_id
                GROUP BY ac.category
            )
            SELECT u.name, ac.category, 
                   SUM(r.quantity * a.emission_factor) as user_category_total,
                   ct.category_total,
                   ROUND((SUM(r.quantity * a.emission_factor) / ct.category_total) * 100, 2) as contribution_pct,
                   RANK() OVER (PARTITION BY ac.category ORDER BY SUM(r.quantity * a.emission_factor) DESC) as rank_in_category
            FROM users u
            JOIN records r ON u.user_id = r.user_id
            JOIN activities a ON r.activity_id = a.activity_id
            JOIN activity_categories ac ON a.activity_id = ac.activity_id
            JOIN category_totals ct ON ac.category = ct.category
            GROUP BY u.user_id, u.name, ac.category, ct.category_total
            HAVING SUM(r.quantity * a.emission_factor) > 0
            ORDER BY ac.category, user_category_total DESC
        """).fetchall()
    
    def query_5_emission_anomaly_detection(self):
        """Query 5: Anomaly detection using statistical functions and subqueries"""
        return self.cursor.execute("""
            WITH emission_stats AS (
                SELECT r.record_id, u.name, a.activity_name, r.date,
                       (r.quantity * a.emission_factor) as emission,
                       AVG(r.quantity * a.emission_factor) OVER (PARTITION BY a.activity_id) as avg_emission,
                       (SELECT AVG(sub_r.quantity * sub_a.emission_factor) 
                        FROM records sub_r 
                        JOIN activities sub_a ON sub_r.activity_id = sub_a.activity_id 
                        WHERE sub_a.activity_id = a.activity_id) as global_avg,
                       (SELECT COUNT(*) * SUM((sub_r.quantity * sub_a.emission_factor) * (sub_r.quantity * sub_a.emission_factor)) - 
                               SUM(sub_r.quantity * sub_a.emission_factor) * SUM(sub_r.quantity * sub_a.emission_factor)
                        FROM records sub_r 
                        JOIN activities sub_a ON sub_r.activity_id = sub_a.activity_id 
                        WHERE sub_a.activity_id = a.activity_id) / 
                       (SELECT COUNT(*) * (COUNT(*) - 1) 
                        FROM records sub_r2 
                        WHERE sub_r2.activity_id = a.activity_id) as variance
                FROM records r
                JOIN users u ON r.user_id = u.user_id
                JOIN activities a ON r.activity_id = a.activity_id
            )
            SELECT record_id, name, activity_name, date, emission, avg_emission,
                   ABS(emission - avg_emission) as deviation,
                   CASE 
                       WHEN ABS(emission - avg_emission) > (2 * SQRT(variance)) THEN 'High Anomaly'
                       WHEN ABS(emission - avg_emission) > (1.5 * SQRT(variance)) THEN 'Medium Anomaly'
                       ELSE 'Normal'
                   END as anomaly_level
            FROM emission_stats
            WHERE ABS(emission - avg_emission) > (1.5 * SQRT(variance))
            ORDER BY deviation DESC
        """).fetchall()
    
    def query_6_seasonal_pattern_analysis(self):
        """Query 6: Seasonal pattern analysis with complex date functions"""
        return self.cursor.execute("""
            WITH seasonal_data AS (
                SELECT 
                    CASE 
                        WHEN CAST(strftime('%m', r.date) AS INTEGER) IN (12, 1, 2) THEN 'Winter'
                        WHEN CAST(strftime('%m', r.date) AS INTEGER) IN (3, 4, 5) THEN 'Spring'
                        WHEN CAST(strftime('%m', r.date) AS INTEGER) IN (6, 7, 8) THEN 'Summer'
                        ELSE 'Autumn'
                    END as season,
                    strftime('%Y', r.date) as year,
                    a.activity_name,
                    SUM(r.quantity * a.emission_factor) as seasonal_emission,
                    COUNT(r.record_id) as activity_count,
                    AVG(r.quantity * a.emission_factor) as avg_emission_per_record
                FROM records r
                JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY season, year, a.activity_name
            ),
            season_comparison AS (
                SELECT season, activity_name,
                       AVG(seasonal_emission) as avg_seasonal_emission,
                       MAX(seasonal_emission) as max_seasonal_emission,
                       MIN(seasonal_emission) as min_seasonal_emission,
                       COUNT(*) as years_data
                FROM seasonal_data
                GROUP BY season, activity_name
            )
            SELECT sc.season, sc.activity_name, sc.avg_seasonal_emission,
                   sc.max_seasonal_emission, sc.min_seasonal_emission,
                   RANK() OVER (PARTITION BY sc.season ORDER BY sc.avg_seasonal_emission DESC) as season_rank,
                   (SELECT AVG(avg_seasonal_emission) FROM season_comparison WHERE activity_name = sc.activity_name) as yearly_avg,
                   ROUND(((sc.avg_seasonal_emission - 
                          (SELECT AVG(avg_seasonal_emission) FROM season_comparison WHERE activity_name = sc.activity_name)) /
                          (SELECT AVG(avg_seasonal_emission) FROM season_comparison WHERE activity_name = sc.activity_name)) * 100, 2) as seasonal_variance_pct
            FROM season_comparison sc
            ORDER BY sc.season, sc.avg_seasonal_emission DESC
        """).fetchall()
    
    def query_7_user_behavior_clustering(self):
        """Query 7: User behavior clustering with advanced analytics"""
        return self.cursor.execute("""
            WITH user_behavior AS (
                SELECT u.user_id, u.name,
                       COUNT(DISTINCT a.activity_id) as activity_diversity,
                       SUM(r.quantity * a.emission_factor) as total_emissions,
                       AVG(r.quantity * a.emission_factor) as avg_emission_per_activity,
                       MAX(r.quantity * a.emission_factor) as max_single_emission,
                       COUNT(r.record_id) as total_activities,
                       JULIANDAY('now') - JULIANDAY(MIN(r.date)) as days_active,
                       COUNT(DISTINCT strftime('%Y-%m', r.date)) as active_months
                FROM users u
                JOIN records r ON u.user_id = r.user_id
                JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY u.user_id, u.name
            ),
            behavior_stats AS (
                SELECT *,
                       NTILE(3) OVER (ORDER BY total_emissions) as emission_tier,
                       NTILE(3) OVER (ORDER BY activity_diversity) as diversity_tier,
                       NTILE(3) OVER (ORDER BY total_activities) as frequency_tier,
                       CASE 
                           WHEN total_activities / NULLIF(days_active, 0) > 0.5 THEN 'High Frequency'
                           WHEN total_activities / NULLIF(days_active, 0) > 0.1 THEN 'Medium Frequency'
                           ELSE 'Low Frequency'
                       END as usage_pattern
                FROM user_behavior
            )
            SELECT name, total_emissions, activity_diversity, total_activities,
                   emission_tier, diversity_tier, frequency_tier, usage_pattern,
                   CASE 
                       WHEN emission_tier = 3 AND diversity_tier = 3 THEN 'High Impact Diverse'
                       WHEN emission_tier = 3 AND diversity_tier = 1 THEN 'High Impact Focused'
                       WHEN emission_tier = 1 AND frequency_tier = 3 THEN 'Low Impact Active'
                       WHEN emission_tier = 1 AND frequency_tier = 1 THEN 'Minimal User'
                       ELSE 'Moderate User'
                   END as user_cluster,
                   ROUND(total_activities / NULLIF(days_active, 0), 3) as activity_rate
            FROM behavior_stats
            ORDER BY total_emissions DESC
        """).fetchall()
    
    def query_8_emission_forecasting_data(self):
        """Query 8: Emission forecasting with trend analysis and moving averages"""
        return self.cursor.execute("""
            WITH daily_emissions AS (
                SELECT r.date,
                       SUM(r.quantity * a.emission_factor) as daily_emission,
                       COUNT(r.record_id) as daily_activities
                FROM records r
                JOIN activities a ON r.activity_id = a.activity_id
                GROUP BY r.date
                ORDER BY r.date
            ),
            trend_analysis AS (
                SELECT date, daily_emission, daily_activities,
                       ROW_NUMBER() OVER (ORDER BY date) as day_number,
                       AVG(daily_emission) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as week_moving_avg,
                       AVG(daily_emission) OVER (ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) as month_moving_avg,
                       LAG(daily_emission, 1) OVER (ORDER BY date) as prev_day,
                       LAG(daily_emission, 7) OVER (ORDER BY date) as prev_week_same_day
                FROM daily_emissions
            ),
            regression_data AS (
                SELECT *,
                       (SELECT COUNT(*) FROM trend_analysis) as n,
                       (SELECT SUM(day_number) FROM trend_analysis) as sum_x,
                       (SELECT SUM(daily_emission) FROM trend_analysis) as sum_y,
                       (SELECT SUM(day_number * daily_emission) FROM trend_analysis) as sum_xy,
                       (SELECT SUM(day_number * day_number) FROM trend_analysis) as sum_x2
                FROM trend_analysis
            )
            SELECT date, daily_emission, week_moving_avg, month_moving_avg,
                   daily_emission - prev_day as day_change,
                   daily_emission - prev_week_same_day as week_change,
                   ROUND(((sum_xy * n - sum_x * sum_y) / (sum_x2 * n - sum_x * sum_x)), 4) as trend_slope,
                   ROUND(((sum_y - ((sum_xy * n - sum_x * sum_y) / (sum_x2 * n - sum_x * sum_x)) * sum_x) / n), 2) as trend_intercept,
                   CASE 
                       WHEN daily_emission > month_moving_avg * 1.2 THEN 'Above Trend'
                       WHEN daily_emission < month_moving_avg * 0.8 THEN 'Below Trend'
                       ELSE 'On Trend'
                   END as trend_status
            FROM regression_data
            WHERE date >= date('now', '-90 days')
            ORDER BY date DESC
        """).fetchall()
    
    def query_9_carbon_efficiency_analysis(self):
        """Query 9: Carbon efficiency analysis with complex calculations"""
        return self.cursor.execute("""
            WITH activity_efficiency AS (
                SELECT a.activity_name, a.unit, a.emission_factor,
                       COUNT(r.record_id) as usage_frequency,
                       SUM(r.quantity) as total_quantity,
                       SUM(r.quantity * a.emission_factor) as total_emissions,
                       AVG(r.quantity) as avg_quantity_per_use,
                       MIN(r.quantity) as min_quantity,
                       MAX(r.quantity) as max_quantity,
                       COUNT(DISTINCT r.user_id) as unique_users
                FROM activities a
                JOIN records r ON a.activity_id = r.activity_id
                GROUP BY a.activity_id, a.activity_name, a.unit, a.emission_factor
            ),
            efficiency_metrics AS (
                SELECT *,
                       total_emissions / NULLIF(usage_frequency, 0) as emission_per_use,
                       total_emissions / NULLIF(unique_users, 0) as emission_per_user,
                       (max_quantity - min_quantity) / NULLIF(avg_quantity_per_use, 0) as quantity_variability,
                       RANK() OVER (ORDER BY emission_factor DESC) as emission_factor_rank,
                       RANK() OVER (ORDER BY total_emissions DESC) as total_emission_rank,
                       RANK() OVER (ORDER BY usage_frequency DESC) as frequency_rank
                FROM activity_efficiency
            ),
            comparative_analysis AS (
                SELECT *,
                       (SELECT AVG(emission_factor) FROM efficiency_metrics) as avg_emission_factor,
                       (SELECT AVG(total_emissions) FROM efficiency_metrics) as avg_total_emissions,
                       CASE 
                           WHEN emission_factor > (SELECT AVG(emission_factor) FROM efficiency_metrics) * 1.5 THEN 'High Carbon Intensity'
                           WHEN emission_factor < (SELECT AVG(emission_factor) FROM efficiency_metrics) * 0.5 THEN 'Low Carbon Intensity'
                           ELSE 'Medium Carbon Intensity'
                       END as carbon_intensity_category
                FROM efficiency_metrics
            )
            SELECT activity_name, unit, emission_factor, usage_frequency, total_emissions,
                   emission_per_use, emission_per_user, carbon_intensity_category,
                   emission_factor_rank, total_emission_rank, frequency_rank,
                   ROUND((emission_factor / avg_emission_factor - 1) * 100, 2) as factor_vs_avg_pct,
                   ROUND((total_emissions / avg_total_emissions - 1) * 100, 2) as total_vs_avg_pct,
                   CASE 
                       WHEN emission_factor_rank <= 3 AND total_emission_rank <= 3 THEN 'Priority Reduction Target'
                       WHEN frequency_rank <= 3 AND emission_factor_rank > (SELECT COUNT(*)/2 FROM efficiency_metrics) THEN 'Optimization Opportunity'
                       ELSE 'Monitor'
                   END as recommendation
            FROM comparative_analysis
            ORDER BY total_emissions DESC
        """).fetchall()
    
    def query_10_comprehensive_impact_assessment(self):
        """Query 10: Comprehensive environmental impact assessment with multiple metrics"""
        return self.cursor.execute("""
            WITH impact_calculations AS (
                SELECT u.name, a.activity_name, r.date, r.quantity, a.unit,
                       (r.quantity * a.emission_factor) as co2_emission,
                       (r.quantity * a.emission_factor) / 22.0 as trees_needed_offset,
                       (r.quantity * a.emission_factor) / 0.404 as equivalent_car_miles,
                       (r.quantity * a.emission_factor) * 0.000453592 as equivalent_tons,
                       CASE a.activity_name
                           WHEN 'Electricity Usage' THEN r.quantity * 0.0007  -- Water usage per kWh
                           WHEN 'Car Travel' THEN r.quantity * 0.2  -- Fuel consumption
                           ELSE 0
                       END as secondary_resource_impact
                FROM users u
                JOIN records r ON u.user_id = r.user_id
                JOIN activities a ON r.activity_id = a.activity_id
            ),
            user_impact_summary AS (
                SELECT name,
                       COUNT(*) as total_activities,
                       SUM(co2_emission) as total_co2,
                       SUM(trees_needed_offset) as total_trees_needed,
                       SUM(equivalent_car_miles) as total_car_miles_equivalent,
                       SUM(equivalent_tons) as total_tons,
                       SUM(secondary_resource_impact) as total_secondary_impact,
                       AVG(co2_emission) as avg_co2_per_activity,
                       MAX(co2_emission) as max_single_emission,
                       COUNT(DISTINCT activity_name) as activity_types,
                       MIN(date) as first_activity_date,
                       MAX(date) as last_activity_date
                FROM impact_calculations
                GROUP BY name
            ),
            global_benchmarks AS (
                SELECT 
                    (SELECT AVG(total_co2) FROM user_impact_summary) as global_avg_co2,
                    (SELECT MAX(total_co2) FROM user_impact_summary) as global_max_co2,
                    (SELECT MIN(total_co2) FROM user_impact_summary) as global_min_co2,
                    (SELECT SUM(total_co2) FROM user_impact_summary) as global_total_co2
            )
            SELECT uis.name, uis.total_co2, uis.total_trees_needed, uis.total_car_miles_equivalent,
                   uis.activity_types, uis.total_activities, uis.avg_co2_per_activity,
                   ROUND((uis.total_co2 / gb.global_total_co2) * 100, 2) as contribution_to_total_pct,
                   ROUND((uis.total_co2 / gb.global_avg_co2), 2) as vs_average_ratio,
                   CASE 
                       WHEN uis.total_co2 > gb.global_avg_co2 * 2 THEN 'High Impact User'
                       WHEN uis.total_co2 > gb.global_avg_co2 THEN 'Above Average User'
                       WHEN uis.total_co2 > gb.global_avg_co2 * 0.5 THEN 'Below Average User'
                       ELSE 'Low Impact User'
                   END as impact_category,
                   ROUND(uis.total_co2 * 3.67, 2) as co2_equivalent_kg,  -- CO2 to CO2e conversion
                   ROUND(uis.total_trees_needed * 50, 2) as forest_area_needed_sqm,  -- Approximate forest area
                   JULIANDAY(uis.last_activity_date) - JULIANDAY(uis.first_activity_date) as tracking_period_days,
                   ROUND(uis.total_co2 / NULLIF((JULIANDAY(uis.last_activity_date) - JULIANDAY(uis.first_activity_date)), 0), 3) as daily_avg_emission
            FROM user_impact_summary uis
            CROSS JOIN global_benchmarks gb
            ORDER BY uis.total_co2 DESC
        """).fetchall()

# Usage functions for integration with main app
def get_all_complex_queries(db_connection):
    """Execute all complex queries and return results"""
    cq = ComplexQueries(db_connection)
    
    results = {
        'user_rankings': cq.query_1_user_ranking_with_percentiles(),
        'monthly_growth': cq.query_2_monthly_growth_analysis(),
        'activity_correlations': cq.query_3_activity_correlation_matrix(),
        'top_contributors': cq.query_4_top_contributors_by_category(),
        'anomaly_detection': cq.query_5_emission_anomaly_detection(),
        'seasonal_patterns': cq.query_6_seasonal_pattern_analysis(),
        'user_clustering': cq.query_7_user_behavior_clustering(),
        'forecasting_data': cq.query_8_emission_forecasting_data(),
        'efficiency_analysis': cq.query_9_carbon_efficiency_analysis(),
        'impact_assessment': cq.query_10_comprehensive_impact_assessment()
    }
    
    return results