from django.core.management.base import BaseCommand
from django.apps import apps
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Disable performance tracking and clean up related metrics'

    def handle(self, *args, **options):
        # Import models here to avoid circular imports
        PerformanceSettings = apps.get_model('performance', 'PerformanceSettings')
        UserSettings = apps.get_model('users', 'UserSettings')
        MetricValue = apps.get_model('metrics', 'MetricValue')
        
        # 1. Disable performance at system level
        settings, created = PerformanceSettings.objects.get_or_create(pk=1)
        settings.updates_enabled = False
        settings.save()
        self.stdout.write(self.style.SUCCESS('Disabled system-wide performance tracking'))
        
        # 2. Disable performance for all users
        user_count = UserSettings.objects.filter(performance_enabled=True).count()
        UserSettings.objects.update(performance_enabled=False)
        self.stdout.write(self.style.SUCCESS(f'Disabled performance tracking for {user_count} users'))
        
        # 3. Deactivate performance metric types using the configure_metrics command
        performance_metric_keys = [
            'position_gain', 'position_gain_percentage', 
            'portfolio_return', 'portfolio_return_percentage'
        ]
        
        # Call the configure_metrics command to deactivate metrics
        call_command('configure_metrics', deactivate=performance_metric_keys)
        self.stdout.write(self.style.SUCCESS(f'Deactivated performance metrics'))
        
        # 4. Option to clear metric values
        if options.get('clear_data', False):
            # Get performance metric types
            MetricType = apps.get_model('metrics', 'MetricType')
            performance_metrics = MetricType.objects.filter(key__in=performance_metric_keys)
            metric_type_ids = performance_metrics.values_list('metric_id', flat=True)
            
            # Delete metric values for these types
            deleted_count = MetricValue.objects.filter(metric_type_id__in=metric_type_ids).delete()[0]
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} performance metric values'))
            
            # Also delete performance metrics
            from performance.services import PerformanceService
            PerformanceService.clear_all_performance_data()
            self.stdout.write(self.style.SUCCESS('Cleared all performance data'))
        
        self.stdout.write(self.style.SUCCESS('Performance module successfully disabled'))

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-data',
            action='store_true',
            help='Clear all performance metric values from the database',
        ) 