from django.core.management.base import BaseCommand
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize app settings for all modules or a specific module'

    def add_arguments(self, parser):
        parser.add_argument(
            '--module',
            type=str,
            help='Initialize settings for a specific module (e.g., "performance", "market_data")',
        )
        parser.add_argument(
            '--state',
            type=str,
            choices=['enabled', 'disabled'],
            default='enabled',
            help='The state to set for the setting (enabled or disabled)',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all settings modules',
        )

    def handle(self, *args, **options):
        if options['list']:
            self._list_settings_modules()
            return
            
        # Determine the desired state
        enabled = options['state'] == 'enabled'
        
        # Initialize settings for a specific module or all modules
        module_name = options.get('module')
        if module_name:
            self._initialize_module_settings(module_name, enabled)
        else:
            self._initialize_all_settings(enabled)
            
    def _list_settings_modules(self):
        """List all app modules with settings models"""
        settings_modules = []
        
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                if model.__name__.endswith('Settings') and hasattr(model, 'updates_enabled'):
                    settings_modules.append({
                        'app': app_config.label,
                        'model': model.__name__,
                        'instance_exists': model.objects.exists() if hasattr(model, 'objects') else False
                    })
        
        self.stdout.write(self.style.SUCCESS(f"Found {len(settings_modules)} app settings modules:"))
        for module in settings_modules:
            status = "exists" if module['instance_exists'] else "not initialized"
            self.stdout.write(f"  - {module['app']}.{module['model']} ({status})")
            
    def _initialize_module_settings(self, module_name, enabled=True):
        """Initialize settings for a specific module"""
        settings_model = None
        
        # Try to find the settings model for the given module
        for app_config in apps.get_app_configs():
            if app_config.label == module_name:
                for model in app_config.get_models():
                    if model.__name__.endswith('Settings') and hasattr(model, 'updates_enabled'):
                        settings_model = model
                        break
                break
        
        if not settings_model:
            self.stdout.write(self.style.ERROR(f"No settings model found for module '{module_name}'"))
            return
            
        # Initialize or update the settings
        settings, created = settings_model.objects.get_or_create(pk=1)
        if created or settings.updates_enabled != enabled:
            settings.updates_enabled = enabled
            settings.save()
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(
                f"{action} {module_name} settings with updates_enabled={enabled}"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"{module_name} settings already set to updates_enabled={enabled}"
            ))
            
    def _initialize_all_settings(self, enabled=True):
        """Initialize settings for all modules with settings models"""
        initialized_count = 0
        
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                if model.__name__.endswith('Settings') and hasattr(model, 'updates_enabled'):
                    settings, created = model.objects.get_or_create(pk=1)
                    if created or settings.updates_enabled != enabled:
                        settings.updates_enabled = enabled
                        settings.save()
                        action = "Created" if created else "Updated"
                        self.stdout.write(self.style.SUCCESS(
                            f"{action} {app_config.label}.{model.__name__} with updates_enabled={enabled}"
                        ))
                        initialized_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"Initialized {initialized_count} app settings modules with updates_enabled={enabled}"
        )) 