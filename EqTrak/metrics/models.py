from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class MetricType(models.Model):
    CATEGORIES = [
        ('MARKET_DATA', 'Market Data'),
        ('FUNDAMENTAL', 'Fundamental'),
        ('TECHNICAL', 'Technical'),
        ('POSITION', 'Position')
    ]
    
    DATA_TYPES = [
        ('PRICE', 'Price'),
        ('RATIO', 'Ratio'),
        ('VOLUME', 'Volume'),
        ('PERCENTAGE', 'Percentage'),
        ('SHARES', 'Shares'),
        ('CURRENCY', 'Currency')
    ]
    
    COMPUTATION_SOURCES = [
        ('shares', 'Total Shares'),
        ('avg_price', 'Average Price'),
        ('cost_basis', 'Cost Basis'),
        ('current_value', 'Current Value'),
        ('position_gain', 'Position Gain/Loss'),
    ]
    
    metric_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    description = models.TextField(blank=True, null=True)
    is_system = models.BooleanField(default=False)
    is_computed = models.BooleanField(default=False)
    computation_source = models.CharField(max_length=50, choices=COMPUTATION_SOURCES, null=True, blank=True)
    computation_dependencies = models.ManyToManyField('self', symmetrical=False, blank=True)
    computation_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['computation_order', 'name']

    def compute_value(self, position):
        """Compute the metric value for a position"""
        if not self.is_computed:
            return None
            
        if self.computation_source == 'shares':
            return self._compute_shares(position)
        elif self.computation_source == 'avg_price':
            return self._compute_avg_price(position)
        elif self.computation_source == 'cost_basis':
            return self._compute_cost_basis(position)
        elif self.computation_source == 'current_value':
            return self._compute_current_value(position)
        elif self.computation_source == 'position_gain':
            return self._compute_gain(position)
        return None

    def _compute_shares(self, position):
        """Calculate total shares from transactions"""
        transactions = position.transaction_set.filter(status='COMPLETED')
        total_shares = sum(t.shares_impact for t in transactions)
        return total_shares

    def _compute_avg_price(self, position):
        """Calculate average purchase price"""
        shares = self._get_dependency_value(position, 'shares')
        if not shares or shares == 0:
            return 0
            
        transactions = position.transaction_set.filter(
            status='COMPLETED',
            transaction_type='BUY'
        )
        total_cost = sum(t.total_with_fees for t in transactions)
        total_shares_bought = sum(t.quantity for t in transactions)
        
        return total_cost / total_shares_bought if total_shares_bought > 0 else 0

    def _compute_cost_basis(self, position):
        """Calculate total cost basis"""
        shares = self._get_dependency_value(position, 'shares')
        avg_price = self._get_dependency_value(position, 'avg_price')
        
        if shares is None or avg_price is None:
            return None
            
        return shares * avg_price

    def _compute_current_value(self, position):
        """Calculate current position value"""
        shares = self._get_dependency_value(position, 'shares')
        market_price = position.get_latest_market_price()
        
        if shares is None or market_price is None:
            return None
            
        return shares * market_price

    def _compute_gain(self, position):
        """Calculate percentage gain/loss"""
        cost_basis = self._get_dependency_value(position, 'cost_basis')
        current_value = self._get_dependency_value(position, 'current_value')
        
        if not cost_basis or cost_basis == 0 or current_value is None:
            return None
            
        gain = ((current_value - cost_basis) / cost_basis) * 100
        return round(gain, 2)

    def _get_dependency_value(self, position, computation_source):
        """Get the most recent value of a dependency metric"""
        dependency = MetricType.objects.filter(
            computation_source=computation_source,
            is_system=True
        ).first()
        
        if not dependency:
            return None
            
        # If it's computed, compute it now
        if dependency.is_computed:
            return dependency.compute_value(position)
            
        # Otherwise get the stored value
        latest_value = MetricValue.objects.filter(
            position=position,
            metric_type=dependency
        ).order_by('-date').first()
        
        return latest_value.value if latest_value else None

class MetricValue(models.Model):
    SCENARIOS = [
        ('BASE', 'Base Case'),
        ('BULL', 'Bull Case'),
        ('BEAR', 'Bear Case')
    ]
    
    value_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.ForeignKey('portfolio.Position', on_delete=models.CASCADE)
    metric_type = models.ForeignKey(MetricType, on_delete=models.CASCADE)
    date = models.DateField()
    value = models.DecimalField(max_digits=15, decimal_places=6)
    source = models.CharField(max_length=50, default='USER')
    confidence = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True
    )
    is_forecast = models.BooleanField(default=False)
    scenario = models.CharField(max_length=10, choices=SCENARIOS, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.metric_type.name} for {self.position.ticker} on {self.date}"
