# Generated migration to remove Section table if it exists
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0022_promocode_is_sitewide'),
    ]

    operations = [
        # Drop the Section table if it exists (from a previous codebase)
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS myApp_section;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

