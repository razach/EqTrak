### 3. Create a Data Migration for Settings Initialization

After creating your settings model, create a data migration to initialize it with default values:

```python
# Create a new migration file: your_app/migrations/0002_initialize_settings.py
from django.db import migrations

def initialize_app_settings(apps, schema_editor):
    """
    Initialize the app settings with default values.
    This ensures the settings object exists with updates_enabled=True.
    """
    YourAppSettings = apps.get_model('your_app', 'YourAppSettings')
    if not YourAppSettings.objects.exists():
        YourAppSettings.objects.create(pk=1, updates_enabled=True)
        print("Created initial app settings (enabled)")

def reverse_initialize_settings(apps, schema_editor):
    """
    Reverse the initialization (for migrations backwards).
    """
    YourAppSettings = apps.get_model('your_app', 'YourAppSettings')
    YourAppSettings.objects.filter(pk=1).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('your_app', '0001_initial'),  # Adjust to your previous migration
    ]

    operations = [
        migrations.RunPython(
            initialize_app_settings,
            reverse_initialize_settings
        ),
    ]
```

This ensures that when migrations are run, the settings entry is created with the default value.

### 4. Using the init_app_settings Command

The project includes a management command to initialize or update settings for all app modules:

```bash
# List all available app settings modules
python manage.py init_app_settings --list

# Initialize all app settings (enabled by default)
python manage.py init_app_settings

# Initialize a specific app's settings
python manage.py init_app_settings --module your_app

# Disable a specific app's features
python manage.py init_app_settings --module your_app --state disabled
```

This command is useful for admin operations and is also used during database resets. 