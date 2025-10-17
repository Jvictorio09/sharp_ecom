#!/usr/bin/env python
"""
Script to fix production database migration issues.
This will help identify and fix the missing 'country' column in production.
"""

import os
import sys

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from django.db import connection, transaction
from django.core.management import execute_from_command_line

def check_database_schema():
    """Check what columns exist in the Order table."""
    with connection.cursor() as cursor:
        try:
            # Check if we're using PostgreSQL (production) or SQLite (local)
            if 'postgresql' in connection.settings_dict['ENGINE']:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'myapp_order' 
                    ORDER BY column_name;
                """)
                columns = cursor.fetchall()
                print("🔍 PostgreSQL Database Schema:")
                print("=" * 50)
                for col_name, col_type in columns:
                    print(f"  {col_name:<25} {col_type}")
                print("=" * 50)
                
                # Check specifically for the 'country' column
                country_exists = any(col[0] == 'country' for col in columns)
                if country_exists:
                    print("✅ 'country' column EXISTS")
                else:
                    print("❌ 'country' column MISSING")
                    return False
                    
            else:
                # SQLite check
                cursor.execute("PRAGMA table_info(myapp_order);")
                columns = cursor.fetchall()
                print("🔍 SQLite Database Schema:")
                print("=" * 50)
                for col in columns:
                    print(f"  {col[1]:<25} {col[2]}")
                print("=" * 50)
                
                # Check specifically for the 'country' column
                country_exists = any(col[1] == 'country' for col in columns)
                if country_exists:
                    print("✅ 'country' column EXISTS")
                else:
                    print("❌ 'country' column MISSING")
                    return False
                    
            return True
            
        except Exception as e:
            print(f"❌ Error checking schema: {e}")
            return False

def run_migrations():
    """Run pending migrations."""
    print("\n🔄 Running migrations...")
    try:
        # Check for pending migrations
        print("Checking for pending migrations...")
        execute_from_command_line(['manage.py', 'showmigrations'])
        
        print("\nRunning migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def main():
    print("=" * 60)
    print("PRODUCTION DATABASE FIX")
    print("=" * 60)
    
    # Check current database
    print(f"📊 Current database: {connection.settings_dict['ENGINE']}")
    print(f"📊 Database name: {connection.settings_dict['NAME']}")
    
    # Check schema
    schema_ok = check_database_schema()
    
    if not schema_ok:
        print("\n🔧 FIXING MISSING COLUMNS...")
        print("Running migrations to add missing columns...")
        
        if run_migrations():
            print("\n✅ Database schema fixed!")
            # Check again
            print("\n🔍 Re-checking schema...")
            check_database_schema()
        else:
            print("\n❌ Failed to fix database schema")
            print("\n📝 MANUAL FIX REQUIRED:")
            print("1. Connect to your production database")
            print("2. Run: python manage.py migrate")
            print("3. Or manually add the missing column:")
            print("   ALTER TABLE myapp_order ADD COLUMN country VARCHAR(2);")
            sys.exit(1)
    else:
        print("\n✅ Database schema is correct!")
    
    print("\n" + "=" * 60)
    print("Database check completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
