from django.apps import AppConfig
import logging
import os

logger = logging.getLogger(__name__)

class PerformanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'performance'
    verbose_name = 'Performance Tracking'
    
    def ready(self):
        """
        Initialize the app when Django starts.
        Register performance metric providers with the metrics system.
        """
        # Import and register performance metric providers
        from .providers import register_providers
        register_providers()
        
        # Apply patches
        import performance.patches
        
        # Import signals
        import performance.signals
        
        # Load metrics configuration (if not being loaded elsewhere)
        self.load_performance_metrics()
        
        # Load performance settings
        self.load_performance_settings()
    
    def load_performance_settings(self):
        """
        Load performance settings from fixtures.
        This ensures default settings are available.
        """
        try:
            # Only run if database is ready
            from django.db import connection
            if not connection.is_usable():
                logger.warning("Database connection not usable, skipping settings configuration")
                return
                
            from django.db.utils import ProgrammingError, OperationalError
            from django.core.management import call_command
            
            try:
                # Check if settings already exist
                from performance.models import PerformanceSettings
                if not PerformanceSettings.objects.exists():
                    logger.info("Loading performance settings from fixtures")
                    call_command('loaddata', 'performance/fixtures/settings.json')
                    logger.info("Performance settings loaded successfully")
            except (ProgrammingError, OperationalError) as e:
                # This can happen during migrations when the settings table doesn't exist yet
                logger.warning(f"Could not load settings: {str(e)}")
        except ImportError:
            # This can happen during testing or when database is not configured
            logger.warning("Could not import database modules, skipping settings configuration")
            pass
    
    def load_performance_metrics(self):
        """
        Load performance metrics from fixtures.
        Since the app is in development, we always load metrics from fixtures.
        
        Skips loading if SKIP_AUTO_METRICS_LOAD environment variable is set.
        This prevents duplicate loading when configure_metrics is called directly.
        """
        # Skip loading if environment variable is set
        if os.environ.get('SKIP_AUTO_METRICS_LOAD'):
            logger.info("Skipping automatic metrics loading due to SKIP_AUTO_METRICS_LOAD")
            return
            
        try:
            # Only run if database is ready
            from django.db import connection
            if not connection.is_usable():
                logger.warning("Database connection not usable, skipping metrics configuration")
                return
                
            from django.db.utils import ProgrammingError, OperationalError
            from django.core.management import call_command
            
            try:
                logger.info("Loading performance metrics from fixtures")
                call_command('configure_metrics', load=True, module='performance', sync=True)
                logger.info("Performance metrics loaded successfully")
            except (ProgrammingError, OperationalError) as e:
                # This can happen during migrations when the metrics table doesn't exist yet
                logger.warning(f"Could not load metrics: {str(e)}")
        except ImportError:
            # This can happen during testing or when database is not configured
            logger.warning("Could not import database modules, skipping metrics configuration")
            pass
