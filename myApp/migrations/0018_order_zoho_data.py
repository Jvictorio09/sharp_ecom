# Generated manually for Zoho integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0017_product_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='zoho_data',
            field=models.JSONField(blank=True, default=dict, help_text='Stores Zoho IDs: {salesorder_id, invoice_id, contact_id, synced_at}'),
        ),
    ]

