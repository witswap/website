# Generated by Django 3.2.3 on 2021-09-24 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('witswap', '0010_configuration_minimum_swap_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='minimum_burn_amount',
            field=models.BigIntegerField(default=10000000000000, help_text='Remember to add the 9 decimals'),
        ),
    ]
