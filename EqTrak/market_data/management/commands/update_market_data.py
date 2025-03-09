from django.core.management.base import BaseCommand
import logging

from market_data.tasks import update_price_data_for_active_securities
from market_data.models import Security, MarketDataSettings
from market_data.services import MarketDataService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update price data for active securities'

    def add_arguments(self, parser):
        parser.add_argument('--symbol', type=str, help='Update a specific security by symbol')
        parser.add_argument('--force', action='store_true', help='Force update even if updates are disabled')
        
    def handle(self, *args, **options):
        symbol = options.get('symbol')
        force = options.get('force', False)
        
        # Check if updates are enabled
        if not MarketDataSettings.is_updates_enabled() and not force:
            self.stdout.write(self.style.WARNING("Market data updates are currently disabled. Use --force to override."))
            return
            
        if symbol:
            try:
                security = Security.objects.get(symbol__iexact=symbol)
                self.stdout.write(f"Updating data for {security.symbol}...")
                if MarketDataService.refresh_security_data(security, user=None):
                    self.stdout.write(self.style.SUCCESS(f"Successfully updated {security.symbol}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to update {security.symbol}"))
            except Security.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Security not found: {symbol}"))
        else:
            self.stdout.write("Updating price data for all active securities...")
            updated, failed = update_price_data_for_active_securities(user=None)
            self.stdout.write(self.style.SUCCESS(f"Updated: {updated}, Failed: {failed}"))

