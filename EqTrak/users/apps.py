from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        """
        Initialize the users app.
        Checks for test users in development environments.
        """
        # Import signals if needed
        # import users.signals
        
        # Check for test users in development
        self.check_test_users()
    
    def check_test_users(self):
        """
        Check if test users exist in development environments.
        Logs a warning if they don't exist.
        """
        try:
            # Only run if database is ready and in normal operation mode
            from django.db import connection
            if not connection.is_usable():
                logger.warning("Database connection not usable, skipping test user check")
                return
                
            from django.db.utils import ProgrammingError, OperationalError
            from django.conf import settings
            
            # Only check in development environments
            is_production = getattr(settings, 'PRODUCTION', False) or getattr(settings, 'ENVIRONMENT', '') == 'production'
            if is_production:
                return
                
            # Check if test users exist
            try:
                from django.core.management import call_command
                call_command('load_test_users', check=True)
                
                # Optionally log a reminder about how to create test users
                logger.info("You can create test users with: python manage.py load_test_users")
            except (ProgrammingError, OperationalError) as e:
                # This can happen during migrations when the users table doesn't exist yet
                logger.warning(f"Could not check test users: {str(e)}")
        except ImportError:
            # This can happen during testing or when database is not configured
            logger.warning("Could not import database modules, skipping test user check")
            pass
