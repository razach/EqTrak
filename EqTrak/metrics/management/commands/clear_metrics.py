from django.core.management.base import BaseCommand
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clear all metrics from the database to avoid duplicates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting',
        )

    def handle(self, *args, **options):
        MetricType = apps.get_model('metrics', 'MetricType')
        MetricValue = apps.get_model('metrics', 'MetricValue')
        
        confirm = options.get('confirm', False)
        
        if not confirm:
            self.stdout.write(
                self.style.WARNING('This will delete ALL metrics and their values from the database.')
            )
            user_input = input('Are you sure you want to continue? [y/N]: ')
            
            if user_input.lower() != 'y':
                self.stdout.write(self.style.SUCCESS('Operation cancelled.'))
                return
        
        # Delete all metric values first (to avoid foreign key constraints)
        metric_value_count = MetricValue.objects.count()
        MetricValue.objects.all().delete()
        
        # Then delete all metric types
        metric_type_count = MetricType.objects.count()
        MetricType.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully cleared {metric_type_count} metric types and {metric_value_count} metric values.'
        ))
        logger.info(f'Cleared {metric_type_count} metric types and {metric_value_count} metric values') 