from django.apps import AppConfig


class MarketDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'market_data'
    verbose_name = 'Market Data'
    
    def ready(self):
        # Import signal handlers when the app is ready
        pass
