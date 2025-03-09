import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class Security(models.Model):
    """
    Represents a tradable security in the market (stocks, ETFs, mutual funds, etc.)
    """
    SECURITY_TYPES = (
        ('stock', _('Stock')),
        ('etf', _('ETF')),
        ('mutual_fund', _('Mutual Fund')),
        ('bond', _('Bond')),
        ('crypto', _('Cryptocurrency')),
        ('other', _('Other')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=20, verbose_name=_('Symbol'))
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    security_type = models.CharField(max_length=20, choices=SECURITY_TYPES, verbose_name=_('Security Type'))
    exchange = models.CharField(max_length=50, blank=True, verbose_name=_('Exchange'))
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Security')
        verbose_name_plural = _('Securities')
        unique_together = ('symbol', 'exchange')
        
    def __str__(self):
        return f"{self.symbol} ({self.name})"
    
    @property
    def latest_price(self):
        """Return the latest available price for this security"""
        latest = self.prices.order_by('-date').first()
        return latest.close if latest else None
        
    @property
    def price_change_1d(self):
        """Calculate 1-day price change percentage"""
        prices = self.prices.order_by('-date')[:2]
        if len(prices) < 2:
            return None
        return (prices[0].close - prices[1].close) / prices[1].close * 100


class PriceData(models.Model):
    """
    Stores historical price data for securities
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    security = models.ForeignKey(Security, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField(verbose_name=_('Date'))
    open = models.DecimalField(max_digits=19, decimal_places=4, verbose_name=_('Open'))
    high = models.DecimalField(max_digits=19, decimal_places=4, verbose_name=_('High'))
    low = models.DecimalField(max_digits=19, decimal_places=4, verbose_name=_('Low'))
    close = models.DecimalField(max_digits=19, decimal_places=4, verbose_name=_('Close'))
    adj_close = models.DecimalField(max_digits=19, decimal_places=4, verbose_name=_('Adjusted Close'))
    volume = models.BigIntegerField(verbose_name=_('Volume'))
    source = models.CharField(max_length=50, default='yahoo', verbose_name=_('Data Source'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Price Data')
        verbose_name_plural = _('Price Data')
        unique_together = ('security', 'date')
        indexes = [
            models.Index(fields=['security', 'date']),
            models.Index(fields=['date']),
        ]
        
    def __str__(self):
        return f"{self.security.symbol} - {self.date}: {self.close}"


class MarketDataSettings(models.Model):
    """
    Stores system-wide settings for market data updates
    """
    updates_enabled = models.BooleanField(default=True, help_text="Enable or disable automatic market data updates")
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Market Data Settings')
        verbose_name_plural = _('Market Data Settings')
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton settings instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    @classmethod
    def is_updates_enabled(cls):
        """Check if market data updates are enabled"""
        return cls.get_instance().updates_enabled
    
    @classmethod
    def set_updates_enabled(cls, enabled):
        """Set the market data updates enabled state"""
        instance = cls.get_instance()
        instance.updates_enabled = enabled
        instance.save()
        return instance
