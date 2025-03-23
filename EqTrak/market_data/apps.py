from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class MarketDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'market_data'
    verbose_name = 'Market Data'
    
    def ready(self):
        """
        Initialize the market data module.
        This runs when Django starts and the app is loaded.
        """
        # Import signal handlers when the app is ready
        import market_data.signals
        
        # Load market data settings
        self.load_market_data_settings()
    
    def load_market_data_settings(self):
        """
        Load market data settings from fixtures.
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
                from market_data.models import MarketDataSettings
                if not MarketDataSettings.objects.exists():
                    logger.info("Loading market data settings from fixtures")
                    call_command('loaddata', 'market_data/fixtures/settings.json')
                    logger.info("Market data settings loaded successfully")
            except (ProgrammingError, OperationalError) as e:
                # This can happen during migrations when the settings table doesn't exist yet
                logger.warning(f"Could not load settings: {str(e)}")
        except ImportError:
            # This can happen during testing or when database is not configured
            logger.warning("Could not import database modules, skipping settings configuration")
            pass
