# Generated by Django 4.2.10 on 2025-03-09 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketDataSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updates_enabled', models.BooleanField(default=True, help_text='Enable or disable automatic market data updates')),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
