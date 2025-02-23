from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid

class MetricType(models.Model):
    SCOPE_TYPES = [
        ('POSITION', 'Position'),
        ('TRANSACTION', 'Transaction'),
        ('PORTFOLIO', 'Portfolio')
    ]
    
    DATA_TYPES = [
        ('PRICE', 'Price'),
        ('RATIO', 'Ratio'),
        ('VOLUME', 'Volume'),
        ('PERCENTAGE', 'Percentage'),
        ('SHARES', 'Shares'),
        ('CURRENCY', 'Currency'),
        ('MEMO', 'Memo')
    ]
    
    COMPUTATION_SOURCES = [
        # Position metrics
        ('shares', 'Total Shares'),
        ('avg_price', 'Average Price'),
        ('cost_basis', 'Cost Basis'),
        ('current_value', 'Current Value'),
        ('position_gain', 'Position Gain/Loss'),
        # Portfolio metrics
        ('total_value', 'Total Portfolio Value'),
        ('cash_balance', 'Cash Balance'),
        ('portfolio_return', 'Portfolio Return'),
        # Transaction metrics
        ('transaction_impact', 'Transaction Impact'),
        ('fee_percentage', 'Fee Percentage')
    ]
    
    metric_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scope_type = models.CharField(max_length=20, choices=SCOPE_TYPES, default='POSITION')
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    description = models.TextField(blank=True, null=True)
    is_system = models.BooleanField(default=False)
    tags = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated tags for organization")
    is_computed = models.BooleanField(default=False)
    computation_source = models.CharField(max_length=50, choices=COMPUTATION_SOURCES, null=True, blank=True)
    computation_dependencies = models.ManyToManyField('self', symmetrical=False, blank=True)
    computation_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['computation_order', 'name']

    @classmethod
    def get_system_metric(cls, name, scope_type=None):
        """Get a system metric by name and optional scope type"""
        query = {'name': name, 'is_system': True}
        if scope_type:
            query['scope_type'] = scope_type
        return cls.objects.filter(**query).first()

    @classmethod
    def get_metrics_for_scope(cls, scope_type, include_system=True):
        """Get all metrics for a specific scope type"""
        query = {'scope_type': scope_type}
        if not include_system:
            query['is_system'] = False
        return cls.objects.filter(**query).order_by('computation_order', 'name')

    def compute_value(self, target_object):
        """Compute the metric value for a target object (position, transaction, or portfolio)"""
        if not self.is_computed:
            return None
            
        # Validate scope type matches target object
        if not self._validate_scope(target_object):
            return None
            
        if self.computation_source == 'shares':
            return self._compute_shares(target_object)
        elif self.computation_source == 'avg_price':
            return self._compute_avg_price(target_object)
        elif self.computation_source == 'cost_basis':
            return self._compute_cost_basis(target_object)
        elif self.computation_source == 'current_value':
            return self._compute_current_value(target_object)
        elif self.computation_source == 'position_gain':
            return self._compute_gain(target_object)
        elif self.computation_source == 'total_value':
            return self._compute_portfolio_value(target_object)
        elif self.computation_source == 'portfolio_return':
            return self._compute_portfolio_return(target_object)
        elif self.computation_source == 'transaction_impact':
            return self._compute_transaction_impact(target_object)
        return None

    def _validate_scope(self, target_object):
        """Validate that the metric scope matches the target object type"""
        from portfolio.models import Position, Portfolio, Transaction
        
        if self.scope_type == 'POSITION' and not isinstance(target_object, Position):
            return False
        elif self.scope_type == 'PORTFOLIO' and not isinstance(target_object, Portfolio):
            return False
        elif self.scope_type == 'TRANSACTION' and not isinstance(target_object, Transaction):
            return False
        return True

    def get_latest_value(self, target_object):
        """Get the most recent value for this metric and target object"""
        return MetricValue.objects.filter(
            metric_type=self,
            **self._get_target_field(target_object)
        ).order_by('-date', '-created_at').first()

    def _get_target_field(self, target_object):
        """Get the field name and value for the target object based on scope"""
        if self.scope_type == 'POSITION':
            return {'position': target_object}
        elif self.scope_type == 'PORTFOLIO':
            return {'portfolio': target_object}
        elif self.scope_type == 'TRANSACTION':
            return {'transaction': target_object}
        return {}

    def _get_dependency_value(self, target_object, computation_source):
        """Get the most recent value of a dependency metric"""
        dependency = MetricType.objects.filter(
            computation_source=computation_source,
            is_system=True,
            scope_type=self.scope_type
        ).first()
        
        if not dependency:
            return None
            
        if dependency.is_computed:
            return dependency.compute_value(target_object)
            
        latest_value = dependency.get_latest_value(target_object)
        return latest_value.value if latest_value else None

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

    def _compute_portfolio_value(self, portfolio):
        """Calculate total portfolio value"""
        total_value = 0
        
        # Get cash balance
        cash_balance = self._get_dependency_value(portfolio, 'cash_balance') or 0
        total_value += cash_balance
        
        # Add up all position values
        for position in portfolio.position_set.filter(is_active=True):
            position_value = position.get_metric_value('Current Value', system_only=True) or 0
            total_value += position_value
        
        return total_value

    def _compute_portfolio_return(self, portfolio):
        """Calculate portfolio return percentage"""
        total_value = self._get_dependency_value(portfolio, 'total_value')
        if not total_value:
            return None
            
        # Calculate total cost basis
        total_cost = 0
        for position in portfolio.position_set.filter(is_active=True):
            position_cost = position.get_metric_value('Cost Basis', system_only=True) or 0
            total_cost += position_cost
            
        # Add cash to both sides of the equation
        cash_balance = self._get_dependency_value(portfolio, 'cash_balance') or 0
        total_value += cash_balance
        total_cost += cash_balance
        
        if total_cost == 0:
            return 0
            
        return ((total_value - total_cost) / total_cost) * 100

    def _compute_transaction_impact(self, transaction):
        """Calculate transaction impact"""
        # Implementation needed
        return None

    def get_values_for_date_range(self, target_object, start_date, end_date=None):
        """Get all values for this metric within a date range"""
        query = {
            'metric_type': self,
            'date__gte': start_date,
            **self._get_target_field(target_object)
        }
        if end_date:
            query['date__lte'] = end_date
        return MetricValue.objects.filter(**query).order_by('date')

class MetricValue(models.Model):
    SCENARIOS = [
        ('BASE', 'Base Case'),
        ('BULL', 'Bull Case'),
        ('BEAR', 'Bear Case')
    ]
    
    value_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Target object references - only one should be set based on metric_type.scope_type
    position = models.ForeignKey('portfolio.Position', on_delete=models.CASCADE, null=True, blank=True)
    portfolio = models.ForeignKey('portfolio.Portfolio', on_delete=models.CASCADE, null=True, blank=True)
    transaction = models.ForeignKey('portfolio.Transaction', on_delete=models.CASCADE, null=True, blank=True)
    
    metric_type = models.ForeignKey(MetricType, on_delete=models.CASCADE)
    date = models.DateField()
    value = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    text_value = models.TextField(null=True, blank=True, help_text="Text content for memo-type metrics")
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
        constraints = [
            # Ensure exactly one target object is set
            models.CheckConstraint(
                check=models.Q(
                    position__isnull=False,
                    portfolio__isnull=True,
                    transaction__isnull=True,
                ) | models.Q(
                    position__isnull=True,
                    portfolio__isnull=False,
                    transaction__isnull=True,
                ) | models.Q(
                    position__isnull=True,
                    portfolio__isnull=True,
                    transaction__isnull=False,
                ),
                name='metric_value_single_target'
            )
        ]
    
    def clean(self):
        """Validate that the metric value has the correct target object for its scope"""
        super().clean()
        
        if not self.metric_type_id:
            return
            
        # Validate that only one target is set
        targets = [
            bool(self.position),
            bool(self.portfolio),
            bool(self.transaction)
        ]
        if sum(targets) != 1:
            raise ValidationError('Exactly one target (position, portfolio, or transaction) must be set')
        
        # Validate that the target matches the metric type's scope
        if self.metric_type.scope_type == 'POSITION' and not self.position:
            raise ValidationError({'position': 'Position is required for position-scoped metrics'})
        elif self.metric_type.scope_type == 'PORTFOLIO' and not self.portfolio:
            raise ValidationError({'portfolio': 'Portfolio is required for portfolio-scoped metrics'})
        elif self.metric_type.scope_type == 'TRANSACTION' and not self.transaction:
            raise ValidationError({'transaction': 'Transaction is required for transaction-scoped metrics'})
        
        # Validate value based on data type
        if self.metric_type.data_type == 'MEMO':
            if not self.text_value and not self.value:
                raise ValidationError('Text value is required for memo-type metrics')
            self.value = None  # Clear numeric value for memo types
        else:
            if not self.value and self.value != 0:
                raise ValidationError('Numeric value is required for non-memo metrics')
            self.text_value = None  # Clear text value for non-memo types
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        target = self.position or self.portfolio or self.transaction
        return f"{self.metric_type.name} for {target} on {self.date}"
