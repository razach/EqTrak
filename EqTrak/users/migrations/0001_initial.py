# Generated by Django 4.2.10 on 2025-03-18 14:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import users.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('market_data_enabled', models.BooleanField(default=True, help_text='Enable or disable market data updates for your account', verbose_name='Enable Market Data')),
                ('market_data_provider', models.CharField(choices=[('system', 'System Default'), ('yahoo', 'Yahoo Finance'), ('alpha_vantage', 'Alpha Vantage')], default='system', help_text='Select which market data provider to use', max_length=20, verbose_name='Market Data Provider')),
                ('alpha_vantage_api_key', users.fields.EncryptedCharField(blank=True, max_length=255, null=True, verbose_name='Alpha Vantage API Key')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Settings',
                'verbose_name_plural': 'User Settings',
            },
        ),
    ]
