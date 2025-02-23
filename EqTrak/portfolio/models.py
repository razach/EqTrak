from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from metrics.models import MetricType, MetricValue

class Portfolio(models.Model):
    portfolio_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def get_metric_value(self, metric_name, system_only=True):
        """Get the latest value for a specific metric"""
        metric = MetricType.get_system_metric(metric_name, 'PORTFOLIO') if system_only else \
                MetricType.objects.filter(name=metric_name, scope_type='PORTFOLIO').first()
        
        if not metric:
            return None
            
        if metric.is_computed:
            return metric.compute_value(self)
            
        latest_value = metric.get_latest_value(self)
        return latest_value.value if latest_value else None

    def get_metric_values(self, metric_name, start_date, end_date=None, system_only=True):
        """Get all values for a specific metric within a date range"""
        metric = MetricType.get_system_metric(metric_name, 'PORTFOLIO') if system_only else \
                MetricType.objects.filter(name=metric_name, scope_type='PORTFOLIO').first()
        
        if not metric:
            return []
            
        return metric.get_values_for_date_range(self, start_date, end_date)

    def get_all_metrics(self, include_system=True):
        """Get all metrics associated with this portfolio"""
        return MetricType.get_metrics_for_scope('PORTFOLIO', include_system)

class Position(models.Model):
    POSITION_TYPES = [
        ('STOCK', 'Stock'),
        ('ETF', 'ETF'),
        ('CRYPTO', 'Cryptocurrency'),
    ]

    position_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    position_type = models.CharField(max_length=10, choices=POSITION_TYPES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ticker} ({self.portfolio.name})"

    @classmethod
    def get_system_metrics(cls):
        """Get all system metrics for positions, ordered by computation order"""
        return MetricType.objects.filter(
            scope_type='POSITION',
            is_system=True
        ).order_by('computation_order', 'name')

    @classmethod
    def get_display_metrics(cls):
        """Get system metrics suitable for table display, excluding memo types"""
        return cls.get_system_metrics().exclude(data_type='MEMO')

    def get_metric_display_value(self, metric_name):
        """Get formatted display value for a metric"""
        value = self.get_metric_value(metric_name)
        if value is None:
            return None
            
        if metric_name in ['Market Price', 'Cost Basis', 'Current Value']:
            return f"{self.portfolio.currency} {value:,.2f}"
        elif metric_name in ['Position Gain/Loss']:
            return f"{value:,.2f}%"
        else:
            return f"{value:,.2f}"

    def get_latest_market_price(self):
        """Get the most recent market price from MetricValue"""
        market_price_metric = MetricType.get_system_metric('Market Price', scope_type='POSITION')
        if not market_price_metric:
            return None
        
        latest_price = market_price_metric.get_latest_value(self)
        return latest_price.value if latest_price else None

    def get_metric_value(self, metric_name, system_only=True):
        """Get the latest value for a specific metric"""
        metric = MetricType.get_system_metric(metric_name, 'POSITION') if system_only else \
                MetricType.objects.filter(name=metric_name, scope_type='POSITION').first()
        
        if not metric:
            return None
            
        if metric.is_computed:
            return metric.compute_value(self)
            
        latest_value = metric.get_latest_value(self)
        return latest_value.value if latest_value else None

    def get_metric_values(self, metric_name, start_date, end_date=None, system_only=True):
        """Get all values for a specific metric within a date range"""
        metric = MetricType.get_system_metric(metric_name, 'POSITION') if system_only else \
                MetricType.objects.filter(name=metric_name, scope_type='POSITION').first()
        
        if not metric:
            return []
            
        return metric.get_values_for_date_range(self, start_date, end_date)

    def get_all_metrics(self, include_system=True):
        """Get all metrics associated with this position"""
        return MetricType.get_metrics_for_scope('POSITION', include_system)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('DIVIDEND', 'Dividend'),
        ('SPLIT', 'Split'),
        ('MERGER', 'Merger'),
    ]
    
    TRANSACTION_STATUS = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed'),
    ]

    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=15, decimal_places=6)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    date = models.DateField()
    settlement_date = models.DateField(null=True)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.position.ticker}"

    @property
    def total_amount(self):
        """Calculate the total amount of the transaction"""
        return self.quantity * self.price if self.quantity and self.price else 0

    @property
    def total_with_fees(self):
        """Calculate the total amount including fees"""
        return self.total_amount + self.fees if self.total_amount is not None else 0

    @property
    def transaction_impact(self):
        """Calculate the impact on position (positive for buys, negative for sells)"""
        if self.transaction_type == 'BUY':
            return self.total_with_fees
        elif self.transaction_type == 'SELL':
            return -self.total_with_fees
        return 0

    @property
    def shares_impact(self):
        """Calculate the impact on shares (positive for buys, negative for sells)"""
        if self.transaction_type == 'BUY':
            return self.quantity
        elif self.transaction_type == 'SELL':
            return -self.quantity
        return 0

    def get_metric_value(self, metric_name, system_only=True):
        """Get the latest value for a specific metric"""
        metric = MetricType.get_system_metric(metric_name, 'TRANSACTION') if system_only else \
                MetricType.objects.filter(name=metric_name, scope_type='TRANSACTION').first()
        
        if not metric:
            return None
            
        if metric.is_computed:
            return metric.compute_value(self)
            
        latest_value = metric.get_latest_value(self)
        return latest_value.value if latest_value else None

    def get_metric_values(self, metric_name, start_date, end_date=None, system_only=True):
        """Get all values for a specific metric within a date range"""
        metric = MetricType.get_system_metric(metric_name, 'TRANSACTION') if system_only else \
                MetricType.objects.filter(name=metric_name, scope_type='TRANSACTION').first()
        
        if not metric:
            return []
            
        return metric.get_values_for_date_range(self, start_date, end_date)

    def get_all_metrics(self, include_system=True):
        """Get all metrics associated with this transaction"""
        return MetricType.get_metrics_for_scope('TRANSACTION', include_system) 