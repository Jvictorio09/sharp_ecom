# Generated manually for promo code tracking

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0018_order_zoho_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='promo_code',
            field=models.CharField(blank=True, help_text='Promo code used for this order', max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='promo_label',
            field=models.CharField(blank=True, help_text="Display label for the promo (e.g., '10% Off')", max_length=255),
        ),
    ]






