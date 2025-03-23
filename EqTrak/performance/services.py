import logging
import functools
from datetime import date
from django.contrib.contenttypes.models import ContentType
from .models import PerformanceSettings, PerformanceMetric
from .integration import (
    store_position_gain_percentage, 
    store_position_gain_absolute,
    store_portfolio_return_percentage,
    store_portfolio_return_absolute,
    store_portfolio_twr,
    store_transaction_gain_percentage,
    store_transaction_gain_absolute,
    is_feature_enabled
)

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
        return PerformanceCalculationService.is_enabled(user=user)
    
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
        
        # Calculate cost basis and current value from position metrics
        positions = portfolio.position_set.all()
        cost_basis = 0
        current_value = 0
        
        # Check if there are any positions at all
        if not positions.exists():
            metric.status_message = "No positions in portfolio. Add positions to track performance."
            metric.save()
            return metric
            
        for position in positions:
            position_cost_basis = position.get_metric_value('Cost Basis')
            position_current_value = position.get_metric_value('Current Value')
            
            if position_cost_basis is not None:
                cost_basis += position_cost_basis
                
            if position_current_value is not None:
                current_value += position_current_value
                
        # If we couldn't get any cost basis information, set a friendly message
        if cost_basis == 0:
            metric.status_message = "No cost basis data available. Add purchase transactions to positions."
            metric.save()
            return metric
            
        # Clear any previous status message since we can now calculate
        metric.status_message = None
        
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
        
        # Update the metrics module with performance values
        
        # Update percentage return
        store_portfolio_return_percentage(portfolio, percentage_gain_loss)
        
        # Update absolute (currency) return
        store_portfolio_return_absolute(portfolio, absolute_gain_loss)
        
        # Calculate and update the time-weighted return
        twr_percentage = PerformanceService.calculate_time_weighted_return(portfolio)
        if twr_percentage is not None:
            store_portfolio_twr(portfolio, twr_percentage)
        
        return metric
    
    @staticmethod
    def calculate_time_weighted_return(portfolio):
        """
        Calculate time-weighted return for a portfolio.
        
        This method accounts for cash flows (deposits and withdrawals) by breaking the
        measurement period into sub-periods and calculating returns for each sub-period.
        
        Args:
            portfolio: Portfolio instance to calculate TWR for
            
        Returns:
            Time-weighted return percentage or None if insufficient data
        """
        from portfolio.models import Transaction
        from django.db.models import Sum, F, Q, Case, When, Value
        from decimal import Decimal
        
        # Get all position transactions in chronological order
        transactions = Transaction.objects.filter(
            position__portfolio=portfolio,
            status='COMPLETED'
        ).order_by('date')
        
        if not transactions.exists():
            return None
            
        # Get start date (first transaction) and end date (today or last valuation)
        start_date = transactions.first().date
        end_date = date.today()
        
        # Calculate cash flows by date
        cash_flows = transactions.values('date').annotate(
            flow=Sum(F('price') * F('quantity') * (
                 Case(
                     When(transaction_type='BUY', then=Value(-1)),
                     When(transaction_type='SELL', then=Value(1)),
                     default=Value(0)
                 )
            ) + F('fees') * (
                 Case(
                     When(transaction_type__in=['BUY', 'SELL'], then=Value(-1)),
                     default=Value(0)
                 )
            ))
        ).order_by('date')
        
        if not cash_flows:
            return None
            
        # Calculate portfolio values at each flow date
        # This is a simplified approach - in a real system you'd need to retrieve 
        # historical market prices for each position to calculate historical values
        
        # For now, we'll use a simplified approach where we use the current metrics
        # and estimate historical values based on transactions
        current_cost_basis = sum(
            position.get_metric_value('Cost Basis') or 0 
            for position in portfolio.position_set.all()
        )
        
        current_value = sum(
            position.get_metric_value('Current Value') or 0 
            for position in portfolio.position_set.all()
        )
        
        if current_cost_basis == 0 or current_value == 0:
            return None
            
        # Calculate a simple rate of return (as a decimal)
        simple_return = (current_value / current_cost_basis) - 1
        
        # Approximate TWR by adjusting for timing of cash flows
        # This is a simplification - a real implementation would need actual historical values
        
        # Calculate weighted time periods for each cash flow
        total_days = (end_date - start_date).days
        if total_days == 0:
            return simple_return * Decimal('100')  # Convert to percentage
            
        # Apply a simple time-weighting to the return
        time_weighted_return = simple_return * Decimal(str(365 / total_days)) if total_days > 0 else simple_return
        
        # Convert to percentage and return
        return time_weighted_return * Decimal('100')
    
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
        
        # Get cost basis from position metrics
        cost_basis = position.get_metric_value('Cost Basis')
        
        # Get current value from position metrics
        current_value = position.get_metric_value('Current Value')
        
        # If either value is missing, we can't calculate performance
        if cost_basis is None or current_value is None:
            logger.warning(f"Missing cost basis or current value for position {position.position_id}")
            
            # Set user-friendly status message
            if cost_basis is None:
                metric.status_message = "No cost basis available. Add a purchase transaction to enable performance tracking."
            elif current_value is None:
                metric.status_message = "No current value available. Add market data to enable performance tracking."
            else:
                metric.status_message = "Unable to calculate performance metrics with the available data."
                
            metric.save()
            return metric
            
        # Clear any previous status message since we can now calculate
        metric.status_message = None
        
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
        
        # Update the metrics module with performance values
        
        # Update percentage gain/loss
        store_position_gain_percentage(position, percentage_gain_loss)
        
        # Update absolute (currency) gain/loss
        store_position_gain_absolute(position, absolute_gain_loss)
        
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
        position_cost_basis = position.get_metric_value('Cost Basis')
        
        if position_cost_basis is None:
            logger.warning(f"Missing cost basis for position {position.position_id} to calculate transaction performance")
            metric.status_message = "No cost basis available for this position. Add purchase transactions."
            metric.save()
            return metric
            
        position_shares = position.get_metric_value('Shares')
        if position_shares is None or position_shares == 0:
            logger.warning(f"Missing or zero shares for position {position.position_id}")
            metric.status_message = "Share count is missing or zero for this position."
            metric.save()
            return metric
            
        # Clear any previous status message since we can now calculate
        metric.status_message = None
        
        # Calculate cost basis proportionally to shares sold
        cost_basis = position_cost_basis * (transaction.quantity / position_shares)
        
        # Sale value is the transaction amount
        sale_value = transaction.total_with_fees
        
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
        
        # Update the metrics module with performance values
        
        # Update percentage gain/loss
        store_transaction_gain_percentage(transaction, percentage_gain_loss)
        
        # Update absolute (currency) gain/loss
        store_transaction_gain_absolute(transaction, absolute_gain_loss)
        
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
            from .integration import PERFORMANCE_METRICS
            
            # Find and delete all performance-related metrics
            for metric_name in PERFORMANCE_METRICS:
                metric_type = MetricType.objects.filter(name=metric_name, is_system=True).first()
                if metric_type:
                    MetricValue.objects.filter(metric_type=metric_type).delete()
                
        except (ImportError, Exception) as e:
            logger.warning(f"Could not clear metric values: {e}")
            
        return True

class PerformanceCalculationService:
    """
    Service providing a clean interface for performance calculations.
    
    This service is designed to be used by the metrics app and provides
    a stable interface for getting performance-related metric values.
    """
    
    @staticmethod
    def is_enabled(user=None):
        """Check if performance calculations are enabled"""
        # Check system-wide setting first
        if not PerformanceSettings.is_feature_enabled():
            return False
            
        # If no user, system setting is sufficient
        if user is None:
            return True
            
        # Check user-specific setting
        try:
            if not user.settings.performance_enabled:
                return False
        except (AttributeError, Exception):
            # If user settings don't exist, default to enabled
            pass
            
        return True
    
    @staticmethod
    def get_position_gain_percentage(position, user=None):
        """
        Get percentage gain/loss for a position.
        
        Args:
            position: Position object
            user: Optional user to check permissions
            
        Returns:
            Percentage gain/loss as a decimal or None if disabled/unavailable
        """
        if not PerformanceService.is_performance_enabled(user=user):
            return None
            
        performance = PerformanceService.calculate_position_performance(position, user=user)
        return performance.percentage_gain_loss if performance else None
    
    @staticmethod
    def get_position_gain_absolute(position, user=None):
        """
        Get absolute (currency) gain/loss for a position.
        
        Args:
            position: Position object
            user: Optional user to check permissions
            
        Returns:
            Absolute gain/loss in currency or None if disabled/unavailable
        """
        if not PerformanceService.is_performance_enabled(user=user):
            return None
            
        performance = PerformanceService.calculate_position_performance(position, user=user)
        return performance.absolute_gain_loss if performance else None
    
    @staticmethod
    def get_portfolio_return_percentage(portfolio, user=None):
        """
        Get percentage return for a portfolio.
        
        Args:
            portfolio: Portfolio object
            user: Optional user to check permissions
            
        Returns:
            Portfolio return percentage as a decimal or None if disabled/unavailable
        """
        if not PerformanceService.is_performance_enabled(user=user):
            return None
            
        performance = PerformanceService.calculate_portfolio_performance(portfolio, user=user)
        return performance.percentage_gain_loss if performance else None
    
    @staticmethod
    def get_portfolio_return_absolute(portfolio, user=None):
        """
        Get absolute (currency) return for a portfolio.
        
        Args:
            portfolio: Portfolio object
            user: Optional user to check permissions
            
        Returns:
            Portfolio return in currency or None if disabled/unavailable
        """
        if not PerformanceService.is_performance_enabled(user=user):
            return None
            
        performance = PerformanceService.calculate_portfolio_performance(portfolio, user=user)
        return performance.absolute_gain_loss if performance else None
    
    @staticmethod
    def get_time_weighted_return_percentage(portfolio, user=None):
        """
        Get time-weighted return percentage for a portfolio.
        
        Args:
            portfolio: Portfolio object
            user: Optional user to check permissions
            
        Returns:
            TWR percentage as a decimal or None if disabled/unavailable
        """
        if not PerformanceService.is_performance_enabled(user=user):
            return None
            
        return PerformanceService.calculate_time_weighted_return(portfolio)
        
    @staticmethod
    def get_transaction_gain_percentage(transaction, user=None):
        """
        Get percentage gain/loss for a transaction.
        Only applicable for sell transactions.
        
        Args:
            transaction: Transaction object
            user: Optional user to check permissions
            
        Returns:
            Percentage gain/loss as a decimal or None if disabled/unavailable
        """
        # Only calculate for sale transactions
        if transaction.transaction_type != 'SELL':
            return None
            
        if not PerformanceService.is_performance_enabled(user=user):
            return None
            
        performance = PerformanceService.calculate_transaction_performance(transaction, user=user)
        return performance.percentage_gain_loss if performance else None 