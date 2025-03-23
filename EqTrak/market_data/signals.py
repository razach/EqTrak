"""
Signal handlers for the market_data app.
These signals allow other components to respond to market data changes.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PriceData

logger = logging.getLogger(__name__)

@receiver(post_save, sender=PriceData)
def price_data_updated(sender, instance, created, **kwargs):
    """
    Signal handler that fires when price data is created or updated.
    This allows other components to respond to price changes.
    """
    action = "created" if created else "updated"
    logger.debug(f"Price data {action}: {instance.security.symbol} at ${instance.close}")
    
    # In the future, additional notification logic could be added here 