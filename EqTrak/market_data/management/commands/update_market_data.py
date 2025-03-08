from django.core.management.base import BaseCommand
import logging

from market_data.tasks import update_price_data_for_active_securities
from market_data.models import Security

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update price data for active securities'

    def add_arguments(self, parser):
        parser.add_argument('--symbol', type=str, help='Update a specific security by symbol')
        
    def handle(self, *args, **options):
        symbol = options.get('symbol')
        
        if symbol:
            try:
                security = Security.objects.get(symbol__iexact=symbol)
                self.stdout.write(f"Updating data for {security.symbol}...")
                from market_data.services import MarketDataService
                if MarketDataService.refresh_security_data(security):
                    self.stdout.write(self.style.SUCCESS(f"Successfully updated {security.symbol}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to update {security.symbol}"))
            except Security.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Security not found: {symbol}"))
        else:
            self.stdout.write("Updating price data for all active securities...")
            updated, failed = update_price_data_for_active_securities()
            self.stdout.write(self.style.SUCCESS(f"Updated: {updated}, Failed: {failed}"))

