import logging
from datetime import date, datetime, timedelta
from typing import Optional, List
import time

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Security, PriceData
from .services import MarketDataService
from .providers.factory import get_provider

logger = logging.getLogger(__name__)

def update_price_data_for_active_securities():
    """
    Update price data for all active securities.
    This function can be called:
    - Manually via management command
    - Scheduled via cron/Celery
    - In response to user refresh request
    """
    logger.info("Updating price data for active securities")
    active_securities = Security.objects.filter(active=True)
    updated = 0
    failed = 0
    
    for security in active_securities:
        try:
            updated_ok = MarketDataService.refresh_security_data(security)
            if updated_ok:
                updated += 1
            else:
                failed += 1
                
            # Prevent hitting rate limits
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error updating {security.symbol}: {e}")
            failed += 1
    
    logger.info(f"Price update completed. Updated: {updated}, Failed: {failed}")
    return updated, failed

def fetch_price_history(security_id, start_date=None, end_date=None):
    """
    Fetch complete price history for a security.
    This is typically used when adding a new security.
    
    Args:
        security_id: UUID of the security
        start_date: Optional start date (defaults to 1 year ago)
        end_date: Optional end date (defaults to today)
    """
    try:
        security = Security.objects.get(id=security_id)
        
        if not end_date:
            end_date = date.today()
            
        if not start_date:
            # Default to 1 year history
            start_date = end_date - timedelta(days=365)
            
        logger.info(f"Fetching price history for {security.symbol} from {start_date} to {end_date}")
        
        provider = get_provider()
        price_data_list = provider.get_historical_prices(
            security.symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        # Process and save the price data
        saved_count = 0
        with transaction.atomic():
            for price_data in price_data_list:
                price_date = date.fromisoformat(price_data['date'])
                PriceData.objects.update_or_create(
                    security=security,
                    date=price_date,
                    defaults={
                        'open': price_data['open'],
                        'high': price_data['high'],
                        'low': price_data['low'],
                        'close': price_data['close'],
                        'adj_close': price_data['adj_close'],
                        'volume': price_data['volume'],
                        'source': provider.__class__.__name__
                    }
                )
                saved_count += 1
        
        logger.info(f"Successfully saved {saved_count} price records for {security.symbol}")
        return saved_count
        
    except Exception as e:
        logger.error(f"Error fetching price history: {e}")
        raise

