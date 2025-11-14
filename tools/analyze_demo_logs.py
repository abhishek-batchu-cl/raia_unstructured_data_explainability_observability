#!/usr/bin/env python3
"""
Analyze Complete Demo Logs - Query All 15 Database Tables
==========================================================

This script queries the database created by demo_complete_all_features.py
and displays metrics from all 15 tables.
"""

import sys
import sqlite3

def print_section(title: str, char: str = "="):
    """Print formatted section header."""
    print("\n" + char * 80)
    print(f"  {title}")
    print(char * 80 + "\n")

def analyze_database(db_path: str):
    """Analyze all tables in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print_section("📊 RAIA DATABASE ANALYSIS - ALL 15 TABLES", "=")
    print(f"Database: {db_path}\n")

    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'raia_%' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"Found {len(tables)} RAIA tables:\n")

    for i, table in enumerate(tables, 1):
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        
        print_section(f"{i}. {table} ({count} rows)", "-")
        
        if count > 0:
            # Get first 3 rows with all columns
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Print column headers
            print("Columns:", ", ".join(column_names))
            print()
            
            # Print first few rows
            for row in rows:
                for col_name, value in zip(column_names, row):
                    # Skip very long text fields
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:97] + "..."
                    print(f"  {col_name}: {value}")
                print()
        else:
            print("  (No data)")
        
    print_section("✅ Analysis Complete", "=")
    print(f"\nSummary:")
    print(f"  Total tables: {len(tables)}")
    
    cursor.execute("SELECT COUNT(*) FROM raia_runs")
    print(f"  Total runs: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM raia_node_metrics")
    print(f"  Total node metrics: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM raia_semantic_scores")
    print(f"  Total semantic scores: {cursor.fetchone()[0]}")
    
    print()

    conn.close()

if __name__ == "__main__":
    db_path = "complete_feature_demo.db"
    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    analyze_database(db_path)
