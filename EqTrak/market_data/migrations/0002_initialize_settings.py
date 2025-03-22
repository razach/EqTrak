from django.db import migrations

def initialize_market_data_settings(apps, schema_editor):
    """
    Initialize the market data settings with default values.
    This ensures the settings object exists with updates_enabled=True.
    """
    MarketDataSettings = apps.get_model('market_data', 'MarketDataSettings')
    if not MarketDataSettings.objects.exists():
        MarketDataSettings.objects.create(pk=1, updates_enabled=True)
        print("Created initial market data settings (enabled)")

def reverse_initialize_settings(apps, schema_editor):
    """
    Reverse the initialization (for migrations backwards).
    """
    MarketDataSettings = apps.get_model('market_data', 'MarketDataSettings')
    MarketDataSettings.objects.filter(pk=1).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('market_data', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            initialize_market_data_settings,
            reverse_initialize_settings
        ),
    ] 