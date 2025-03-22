import logging
import functools
from datetime import date
from django.contrib.contenttypes.models import ContentType
from .models import PerformanceSettings, PerformanceMetric
from .metrics import update_position_gain_loss, update_portfolio_return, is_metric_calculation_enabled

logger = logging.getLogger(__name__)

def check_performance_access(func):
    """
    Decorator to check if access to performance calculations is enabled.
    Checks both system-wide settings and user-specific settings.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Find user parameter
        user = kwargs.get('user')
        
        # Check system-wide setting first
        if not PerformanceSettings.is_feature_enabled():
            logger.info("Performance feature disabled at system level")
            return None
            
        # If no user, system setting is sufficient
        if user is None:
            return func(*args, **kwargs)
            
        # Check user-specific setting
        try:
            if not user.settings.performance_enabled:
                logger.info(f"Performance feature disabled for user {user.username}")
                return None
        except (AttributeError, Exception) as e:
            # If user settings don't exist, default to enabled
            logger.debug(f"Error checking user performance settings: {e}")
            pass
            
        # Feature access allowed, call the function
        return func(*args, **kwargs)
        
    return wrapper


class PerformanceService:
    """
    Service for calculating performance metrics.
    
    This is the ONLY implementation of gain/loss calculations in the system.
    The metrics module delegates all gain/loss calculations to this service.
    """
    
    @staticmethod
    def is_performance_enabled(user=None):
        """
        Check if performance calculations are enabled for the given user.
        System settings override user preferences.
        """
        return is_metric_calculation_enabled(user=user)
    
    @staticmethod
    @check_performance_access
    def calculate_portfolio_performance(portfolio, user=None):
        """
        Calculate performance metrics for a portfolio.
        
        Args:
            portfolio: Portfolio instance to calculate metrics for
            user: User requesting the calculation
            
        Returns:
            PerformanceMetric instance or None if feature is disabled
        """
        # Get or create performance metric for this portfolio
        content_type = ContentType.objects.get_for_model(portfolio)
        metric, created = PerformanceMetric.objects.get_or_create(
            content_type=content_type,
            object_id=portfolio.portfolio_id
        )
        
        # Calculate cost basis and current value from all positions
        positions = portfolio.position_set.all()
        cost_basis = sum(position.cost_basis for position in positions)
        current_value = sum(position.current_value for position in positions)
        
        # Calculate gains/losses
        absolute_gain_loss = current_value - cost_basis
        percentage_gain_loss = 0
        if cost_basis > 0:
            percentage_gain_loss = (absolute_gain_loss / cost_basis) * 100
        
        # Update the metric
        metric.cost_basis = cost_basis
        metric.current_value = current_value
        metric.absolute_gain_loss = absolute_gain_loss
        metric.percentage_gain_loss = percentage_gain_loss
        metric.save()
        
        # Update the metrics module's portfolio return metric
        update_portfolio_return(portfolio, percentage_gain_loss)
        
        return metric
    
    @staticmethod
    @check_performance_access
    def calculate_position_performance(position, user=None):
        """
        Calculate performance metrics for a position.
        
        Args:
            position: The position to calculate metrics for
            user: Optional user to check permission
            
        Returns:
            PerformanceMetric instance or None if feature is disabled
        """
        # Get or create performance metric for this position
        content_type = ContentType.objects.get_for_model(position)
        metric, created = PerformanceMetric.objects.get_or_create(
            content_type=content_type,
            object_id=position.position_id
        )
        
        # Get cost basis from position
        cost_basis = position.cost_basis
        
        # Get current value - if market data is available, use it
        # otherwise use the last known value
        current_value = position.current_value
        
        # Calculate gains/losses
        absolute_gain_loss = current_value - cost_basis
        percentage_gain_loss = 0
        if cost_basis > 0:
            percentage_gain_loss = (absolute_gain_loss / cost_basis) * 100
        
        # Update the metric
        metric.cost_basis = cost_basis
        metric.current_value = current_value
        metric.absolute_gain_loss = absolute_gain_loss
        metric.percentage_gain_loss = percentage_gain_loss
        metric.save()
        
        # Update the metrics module's position gain metric
        update_position_gain_loss(position, percentage_gain_loss)
        
        return metric
    
    @staticmethod
    @check_performance_access
    def calculate_transaction_performance(transaction, user=None):
        """
        Calculate performance metrics for a transaction.
        Only sale transactions have meaningful performance metrics.
        
        Args:
            transaction: The transaction to calculate metrics for
            user: Optional user to check permission
            
        Returns:
            PerformanceMetric instance or None if feature is disabled or not applicable
        """
        # Only calculate for sale transactions
        if transaction.transaction_type != 'SELL':
            return None
        
        # Get or create performance metric for this transaction
        content_type = ContentType.objects.get_for_model(transaction)
        metric, created = PerformanceMetric.objects.get_or_create(
            content_type=content_type,
            object_id=transaction.transaction_id
        )
        
        # For a sale, cost basis is the position's cost basis at time of sale
        # multiplied by the proportion of shares sold
        position = transaction.position
        cost_basis = position.cost_basis * (transaction.shares / position.shares)
        
        # Sale value is the transaction amount
        sale_value = transaction.amount
        
        # Calculate realized gain/loss
        absolute_gain_loss = sale_value - cost_basis
        percentage_gain_loss = 0
        if cost_basis > 0:
            percentage_gain_loss = (absolute_gain_loss / cost_basis) * 100
        
        # Update the metric
        metric.cost_basis = cost_basis
        metric.current_value = sale_value
        metric.absolute_gain_loss = absolute_gain_loss
        metric.percentage_gain_loss = percentage_gain_loss
        metric.is_realized = True
        metric.save()
        
        # Update the metrics module's transaction gain metric
        from .metrics import update_transaction_gain_loss
        update_transaction_gain_loss(transaction, percentage_gain_loss)
        
        return metric
    
    @staticmethod
    @check_performance_access
    def calculate_all_performance(user=None):
        """
        Recalculate all performance metrics.
        
        Args:
            user: Optional user to check permission
            
        Returns:
            Dictionary with counts of metrics updated
        """
        from portfolio.models import Portfolio, Position, Transaction
        
        results = {
            'portfolios': 0,
            'positions': 0,
            'transactions': 0
        }
        
        # Recalculate all portfolio metrics
        portfolios = Portfolio.objects.all()
        for portfolio in portfolios:
            PerformanceService.calculate_portfolio_performance(portfolio, user=user)
            results['portfolios'] += 1
        
        # Recalculate all position metrics
        positions = Position.objects.all()
        for position in positions:
            PerformanceService.calculate_position_performance(position, user=user)
            results['positions'] += 1
        
        # Recalculate all transaction metrics
        transactions = Transaction.objects.filter(transaction_type='SELL')
        for transaction in transactions:
            PerformanceService.calculate_transaction_performance(transaction, user=user)
            results['transactions'] += 1
        
        return results
        
    @staticmethod
    def clear_all_performance_data():
        """
        Clear all performance metrics data.
        
        This can be used when disabling the performance module to clean up data.
        """
        # Delete all performance metrics
        PerformanceMetric.objects.all().delete()
        
        # Optionally, also clear metric values in the metrics module
        try:
            from metrics.models import MetricType, MetricValue
            from .metrics import PERFORMANCE_METRICS
            
            # Find and delete all performance-related metrics
            for metric_name in PERFORMANCE_METRICS:
                metric_type = MetricType.objects.filter(name=metric_name, is_system=True).first()
                if metric_type:
                    MetricValue.objects.filter(metric_type=metric_type).delete()
                
        except (ImportError, Exception) as e:
            logger.warning(f"Could not clear metric values: {e}")
            
        return True 