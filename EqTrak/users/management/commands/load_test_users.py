import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load test users from fixtures for development environments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force loading test users even in production environments',
        )
        parser.add_argument(
            '--check',
            action='store_true',
            help='Only check if test users exist, without creating them',
        )

    def handle(self, *args, **options):
        # Safety check for production environments
        is_production = getattr(settings, 'PRODUCTION', False) or getattr(settings, 'ENVIRONMENT', '') == 'production'
        force = options.get('force', False)
        check_only = options.get('check', False)

        if is_production and not force:
            self.stdout.write(
                self.style.WARNING('Refusing to load test users in a production environment. '
                                  'Use --force to override this safety check.')
            )
            return

        if check_only:
            self._check_test_users()
            return

        # Load test users from fixture
        fixture_path = os.path.join('users', 'fixtures', 'test_users.json')
        
        try:
            # Try to load test users
            call_command('loaddata', fixture_path, verbosity=1)
            self.stdout.write(self.style.SUCCESS('Successfully loaded test users'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading test users: {str(e)}'))
            logger.error(f'Failed to load test users: {str(e)}')
            
    def _check_test_users(self):
        """Check if test users exist in the database"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        test_users = [
            'test_user1',
            'test_user2',
        ]
        
        existing = []
        missing = []
        
        for username in test_users:
            if User.objects.filter(username=username).exists():
                existing.append(username)
            else:
                missing.append(username)
                
        if existing:
            self.stdout.write(self.style.SUCCESS(f'Existing test users: {", ".join(existing)}'))
        
        if missing:
            self.stdout.write(self.style.WARNING(f'Missing test users: {", ".join(missing)}'))
        
        return len(missing) == 0 