from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from portfolio.models import Position, Portfolio, Transaction
from .models import PerformanceMetric
from .services import PerformanceService

@receiver(post_save, sender=Position)
def update_position_performance(sender, instance, created, **kwargs):
    """
    Update performance metrics when a position is created or updated.
    """
    PerformanceService.calculate_position_performance(instance)

@receiver(post_save, sender=Portfolio)
def update_portfolio_performance(sender, instance, created, **kwargs):
    """
    Update performance metrics when a portfolio is created or updated.
    """
    PerformanceService.calculate_portfolio_performance(instance)

@receiver(post_save, sender=Transaction)
def update_transaction_performance(sender, instance, created, **kwargs):
    """
    Update performance metrics when a transaction is created or updated.
    Only calculates for SELL transactions.
    """
    if instance.transaction_type == 'SELL':
        PerformanceService.calculate_transaction_performance(instance)
    
    # Also update the related position and portfolio metrics
    PerformanceService.calculate_position_performance(instance.position)
    PerformanceService.calculate_portfolio_performance(instance.position.portfolio)

@receiver(post_delete, sender=Transaction)
def handle_transaction_delete(sender, instance, **kwargs):
    """
    Update position and portfolio metrics when a transaction is deleted.
    """
    try:
        position = instance.position
        portfolio = position.portfolio
        
        # Update position and portfolio metrics
        PerformanceService.calculate_position_performance(position)
        PerformanceService.calculate_portfolio_performance(portfolio)
        
        # Clean up any performance metrics for this transaction
        content_type = ContentType.objects.get_for_model(instance)
        PerformanceMetric.objects.filter(
            content_type=content_type,
            object_id=instance.id
        ).delete()
    except Exception:
        # Handle case where position or portfolio might be deleted
        pass 