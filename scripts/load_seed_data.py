#!/usr/bin/env python3
"""
Load seed data into the Escher database.
This replaces hardcoded mocks with real business data.
"""

import sqlite3
import os
from pathlib import Path

def load_seed_data():
    """Load seed data from SQL file into the database."""
    
    # Get the database path
    db_path = "bookclose.db"
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Please run create_tables.py first.")
        return
    
    # Read the seed data SQL file
    seed_file = Path("data/seed_data.sql")
    if not seed_file.exists():
        print(f"Seed data file {seed_file} not found.")
        return
    
    with open(seed_file, 'r') as f:
        sql_content = f.read()
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Loading seed data...")
        
        # Split SQL content into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement.startswith('--'):
                continue  # Skip comments
                
            try:
                cursor.execute(statement)
                print(f"  ✓ Executed statement {i}")
            except sqlite3.Error as e:
                print(f"  ✗ Error in statement {i}: {e}")
                print(f"    Statement: {statement[:100]}...")
                continue
        
        # Commit changes
        conn.commit()
        print(f"\n✓ Successfully loaded seed data into {db_path}")
        
        # Verify data was loaded
        cursor.execute("SELECT COUNT(*) FROM compliance_requirements")
        compliance_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vendor_categories")
        vendor_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM coa_templates")
        coa_count = cursor.fetchone()[0]
        
        print("\nData verification:")
        print(f"  - Compliance requirements: {compliance_count}")
        print(f"  - Vendor categories: {vendor_count}")
        print(f"  - Chart of accounts templates: {coa_count}")
        
    except Exception as e:
        print(f"Error loading seed data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    load_seed_data()
