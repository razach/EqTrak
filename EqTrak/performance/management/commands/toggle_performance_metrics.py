from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Toggle activation of performance metrics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--activate',
            action='store_true',
            help='Activate performance metrics',
        )
        parser.add_argument(
            '--deactivate',
            action='store_true',
            help='Deactivate performance metrics',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current status of performance metrics',
        )
        
    def handle(self, *args, **options):
        # Define performance metric keys
        performance_metric_keys = [
            'position_gain', 'position_gain_percentage', 
            'portfolio_return', 'portfolio_return_percentage'
        ]
        
        # Handle status check
        if options.get('status'):
            self._check_metrics_status(performance_metric_keys)
            return
            
        # Handle activation
        if options.get('activate'):
            self._activate_metrics(performance_metric_keys, True)
            return
            
        # Handle deactivation
        if options.get('deactivate'):
            self._activate_metrics(performance_metric_keys, False)
            return
            
        # Default if no options provided
        self.stdout.write(self.style.WARNING(
            "No action specified. Use --activate, --deactivate, or --status to perform an action."
        ))
        
    def _check_metrics_status(self, metric_keys):
        """Check the current status of performance metrics"""
        MetricType = apps.get_model('metrics', 'MetricType')
        
        self.stdout.write(self.style.SUCCESS("Performance Metrics Status:"))
        self.stdout.write("-" * 60)
        
        for key in metric_keys:
            try:
                metric = MetricType.objects.get(key=key)
                status = "ACTIVE" if metric.is_active else "INACTIVE"
                status_style = self.style.SUCCESS if metric.is_active else self.style.WARNING
                self.stdout.write(f"{key:<30} {status_style(status)}")
            except MetricType.DoesNotExist:
                self.stdout.write(f"{key:<30} {self.style.ERROR('NOT FOUND')}")
                
        # Also check PerformanceSettings
        try:
            PerformanceSettings = apps.get_model('performance', 'PerformanceSettings')
            settings = PerformanceSettings.objects.first()
            if settings:
                status = "ENABLED" if settings.updates_enabled else "DISABLED"
                status_style = self.style.SUCCESS if settings.updates_enabled else self.style.WARNING
                self.stdout.write(f"System-wide updates: {status_style(status)}")
        except Exception as e:
            self.stdout.write(f"System-wide updates: {self.style.ERROR('ERROR')}")
            
    def _activate_metrics(self, metric_keys, activate=True):
        """Activate or deactivate performance metrics"""
        action = "Activating" if activate else "Deactivating"
        self.stdout.write(f"{action} performance metrics...")
        
        # Call the configure_metrics command to handle activation/deactivation
        if activate:
            call_command('configure_metrics', activate=metric_keys)
        else:
            call_command('configure_metrics', deactivate=metric_keys)
            
        # Also update PerformanceSettings if deactivating
        if not activate:
            try:
                PerformanceSettings = apps.get_model('performance', 'PerformanceSettings')
                settings, created = PerformanceSettings.objects.get_or_create(pk=1)
                settings.updates_enabled = False
                settings.save()
                self.stdout.write(self.style.SUCCESS("Disabled system-wide performance updates"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating PerformanceSettings: {str(e)}"))
                
        # Update user settings if deactivating
        if not activate:
            try:
                UserSettings = apps.get_model('users', 'UserSettings')
                count = UserSettings.objects.filter(performance_enabled=True).count()
                UserSettings.objects.update(performance_enabled=False)
                self.stdout.write(self.style.SUCCESS(f"Disabled performance for {count} users"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating UserSettings: {str(e)}"))
                
        # Final confirmation
        action = "Activated" if activate else "Deactivated"
        self.stdout.write(self.style.SUCCESS(f"{action} performance metrics successfully")) 