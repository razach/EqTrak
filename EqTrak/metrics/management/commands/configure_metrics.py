import os
import json
import logging
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
from django.apps import apps

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Configure system metrics without requiring migrations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--load',
            action='store_true',
            help='Load standard metrics from fixtures',
        )
        parser.add_argument(
            '--module',
            type=str,
            help='Specifically load metrics for a single module (e.g., "performance")',
        )
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Update existing metrics to match fixture definitions',
        )
        parser.add_argument(
            '--activate',
            type=str,
            nargs='+',
            help='Activate specific metrics by key',
        )
        parser.add_argument(
            '--deactivate',
            type=str,
            nargs='+',
            help='Deactivate specific metrics by key',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all registered metrics',
        )

    def handle(self, *args, **options):
        MetricType = apps.get_model('metrics', 'MetricType')
        
        if options['list']:
            self._list_metrics(MetricType)
            return
            
        if options['load']:
            self._load_metrics(options.get('module'), options.get('sync', False))
            return
            
        if options['activate']:
            self._activate_deactivate_metrics(MetricType, options['activate'], True)
            return
            
        if options['deactivate']:
            self._activate_deactivate_metrics(MetricType, options['deactivate'], False)
            return
            
        # Default behavior if no arguments
        self.stdout.write("No action specified. Use --help to see available options.")
    
    def _list_metrics(self, MetricType):
        """List all registered metrics"""
        metrics = MetricType.objects.all().order_by('scope_type', 'name')
        
        self.stdout.write(self.style.SUCCESS(
            f"{'KEY':<30} {'NAME':<40} {'SCOPE':<12} {'ACTIVE':<8} {'SYSTEM':<8}"
        ))
        self.stdout.write(self.style.SUCCESS("-" * 100))
        
        for metric in metrics:
            self.stdout.write(
                f"{metric.key or '-':<30} {metric.name:<40} {metric.scope_type:<12} "
                f"{'✓' if getattr(metric, 'is_active', True) else '✗':<8} "
                f"{'✓' if metric.is_system else '✗':<8}"
            )
            
        self.stdout.write(self.style.SUCCESS(f"\nTotal: {metrics.count()} metrics"))
    
    def _load_metrics(self, module_name=None, sync=False):
        """Load metrics from fixture files"""
        fixtures_loaded = 0
        
        # Always load standard metrics
        fixtures_loaded += self._load_fixture_file('metrics/fixtures/standard_metrics.json', sync)
        
        # Load module-specific metrics if requested
        if module_name:
            module_fixture = f"{module_name}/fixtures/{module_name}_metrics.json"
            fixtures_loaded += self._load_fixture_file(module_fixture, sync)
        else:
            # Try to load metrics fixtures from all installed apps
            for app_config in apps.get_app_configs():
                fixture_path = f"{app_config.label}/fixtures/{app_config.label}_metrics.json"
                fixtures_loaded += self._load_fixture_file(fixture_path, sync)
                
        self.stdout.write(self.style.SUCCESS(f"Loaded {fixtures_loaded} fixture files"))
    
    def _load_fixture_file(self, relative_path, sync=False):
        """Load a specific fixture file"""
        # Check if file exists in any of the INSTALLED_APPS directories
        for app_config in apps.get_app_configs():
            fixture_path = os.path.join(app_config.path, '..', relative_path)
            if os.path.exists(fixture_path):
                try:
                    # Always use the sync method to avoid duplicate metrics
                    # This ensures we update or create metrics rather than just loading
                    self._sync_fixture(fixture_path)
                    self.stdout.write(self.style.SUCCESS(f"Loaded fixture: {relative_path}"))
                    return 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error loading {relative_path}: {str(e)}"))
        
        return 0
    
    def _sync_fixture(self, fixture_path):
        """
        Sync existing metrics with fixture definitions instead of just loading.
        This updates existing records rather than creating duplicates.
        """
        MetricType = apps.get_model('metrics', 'MetricType')
        
        # Load the fixture data
        with open(fixture_path, 'r') as f:
            fixture_data = json.load(f)
        
        # Sync each metric
        for item in fixture_data:
            if item['model'] != 'metrics.metrictype':
                continue
                
            fields = item['fields']
            
            # Set is_computed=True if computation_source is provided
            if 'computation_source' in fields and fields['computation_source']:
                fields['is_computed'] = True
            
            # Try to find by key first (preferred) or by name+scope if key not available
            if 'key' in fields and fields['key']:
                metric, created = MetricType.objects.update_or_create(
                    key=fields['key'],
                    defaults=fields
                )
            else:
                metric, created = MetricType.objects.update_or_create(
                    name=fields['name'],
                    scope_type=fields['scope_type'],
                    defaults=fields
                )
            
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} metric: {fields.get('name')}")
    
    def _activate_deactivate_metrics(self, MetricType, keys, activate=True):
        """Activate or deactivate metrics by key"""
        action = "Activated" if activate else "Deactivated"
        count = 0
        
        for key in keys:
            metrics = MetricType.objects.filter(key=key)
            if not metrics.exists():
                self.stdout.write(self.style.WARNING(f"No metric found with key: {key}"))
                continue
                
            metrics.update(is_active=activate)
            count += metrics.count()
            
        self.stdout.write(self.style.SUCCESS(f"{action} {count} metrics")) 