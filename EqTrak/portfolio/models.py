from django.db import models
from django.contrib.auth.models import User
import uuid

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
    shares = models.DecimalField(max_digits=15, decimal_places=6, null=True)
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    cost_basis = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ticker} ({self.portfolio.name})"

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