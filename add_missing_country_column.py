#!/usr/bin/env python
"""
Emergency fix: Add missing 'country' column to production database.
Use this if migrations fail.
"""

import os
import sys

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myProject.settings")
import django
django.setup()

from django.db import connection, transaction

def add_missing_columns():
    """Add missing columns directly to the database."""
    print("🔧 Adding missing columns to production database...")
    
    with connection.cursor() as cursor:
        try:
            # Check if we're using PostgreSQL
            if 'postgresql' in connection.settings_dict['ENGINE']:
                print("📊 Using PostgreSQL database")
                
                # Add country column if it doesn't exist
                cursor.execute("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'myapp_order' AND column_name = 'country'
                        ) THEN
                            ALTER TABLE myapp_order ADD COLUMN country VARCHAR(2);
                            RAISE NOTICE 'Added country column';
                        ELSE
                            RAISE NOTICE 'country column already exists';
                        END IF;
                    END $$;
                """)
                
                # Add shipping_address column if it doesn't exist
                cursor.execute("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'myapp_order' AND column_name = 'shipping_address'
                        ) THEN
                            ALTER TABLE myapp_order ADD COLUMN shipping_address JSONB;
                            RAISE NOTICE 'Added shipping_address column';
                        ELSE
                            RAISE NOTICE 'shipping_address column already exists';
                        END IF;
                    END $$;
                """)
                
                # Add shipping_address_text column if it doesn't exist
                cursor.execute("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'myapp_order' AND column_name = 'shipping_address_text'
                        ) THEN
                            ALTER TABLE myapp_order ADD COLUMN shipping_address_text TEXT DEFAULT '';
                            RAISE NOTICE 'Added shipping_address_text column';
                        ELSE
                            RAISE NOTICE 'shipping_address_text column already exists';
                        END IF;
                    END $$;
                """)
                
                print("✅ PostgreSQL columns added successfully!")
                
            else:
                print("📊 Using SQLite database")
                
                # SQLite doesn't support adding columns conditionally, so we'll try and catch
                try:
                    cursor.execute("ALTER TABLE myapp_order ADD COLUMN country VARCHAR(2);")
                    print("✅ Added country column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("ℹ️  country column already exists")
                    else:
                        raise
                
                try:
                    cursor.execute("ALTER TABLE myapp_order ADD COLUMN shipping_address TEXT DEFAULT '{}';")
                    print("✅ Added shipping_address column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("ℹ️  shipping_address column already exists")
                    else:
                        raise
                
                try:
                    cursor.execute("ALTER TABLE myapp_order ADD COLUMN shipping_address_text TEXT DEFAULT '';")
                    print("✅ Added shipping_address_text column")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print("ℹ️  shipping_address_text column already exists")
                    else:
                        raise
                
                print("✅ SQLite columns added successfully!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding columns: {e}")
            return False

def main():
    print("=" * 60)
    print("EMERGENCY DATABASE FIX")
    print("=" * 60)
    
    print(f"📊 Current database: {connection.settings_dict['ENGINE']}")
    print(f"📊 Database name: {connection.settings_dict['NAME']}")
    
    if add_missing_columns():
        print("\n✅ Database columns fixed successfully!")
        print("Your application should now work properly.")
    else:
        print("\n❌ Failed to fix database columns")
        print("Please contact your database administrator or check the error above.")
        sys.exit(1)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
