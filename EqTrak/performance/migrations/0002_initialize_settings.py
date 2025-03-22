from django.db import migrations

def initialize_performance_settings(apps, schema_editor):
    """
    Initialize the performance settings with default values.
    This ensures the settings object exists with updates_enabled=True.
    """
    PerformanceSettings = apps.get_model('performance', 'PerformanceSettings')
    if not PerformanceSettings.objects.exists():
        PerformanceSettings.objects.create(pk=1, updates_enabled=True)
        print("Created initial performance settings (enabled)")

def reverse_initialize_settings(apps, schema_editor):
    """
    Reverse the initialization (for migrations backwards).
    """
    PerformanceSettings = apps.get_model('performance', 'PerformanceSettings')
    PerformanceSettings.objects.filter(pk=1).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('performance', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            initialize_performance_settings,
            reverse_initialize_settings
        ),
    ] 