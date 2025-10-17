# Database Fix Guide

## Problem
Your production database is missing the `country` column in the `myApp_order` table, causing this error:
```
ProgrammingError: column myApp_order.country does not exist
```

## Root Cause
When you switched from SQLite (local) to PostgreSQL (production), the production database didn't have all the migrations applied that your local database had.

## Solutions (Try in Order)

### Option 1: Run Migrations (Recommended)
```bash
# On your production server or Railway console:
python manage.py migrate
```

### Option 2: Emergency Column Addition
If migrations fail, run this emergency fix:
```bash
python add_missing_country_column.py
```

### Option 3: Manual Database Fix
Connect directly to your PostgreSQL database and run:
```sql
ALTER TABLE myapp_order ADD COLUMN country VARCHAR(2);
ALTER TABLE myapp_order ADD COLUMN shipping_address JSONB;
ALTER TABLE myapp_order ADD COLUMN shipping_address_text TEXT DEFAULT '';
```

## Prevention for Future
1. **Always run migrations** after deploying code changes
2. **Test locally** with the same database type as production
3. **Use environment-specific settings** (which we've already set up)

## Current Database Configuration
- **Local**: SQLite (`db_local.sqlite3`)
- **Production**: PostgreSQL (via `DATABASE_URL`)

## Files Created
- `fix_production_database.py` - Diagnostic tool
- `add_missing_country_column.py` - Emergency fix
- `DATABASE_FIX_GUIDE.md` - This guide

## Next Steps
1. Deploy the updated `settings.py` to production
2. Run migrations on production
3. Test your application
4. Keep local and production databases separate going forward
