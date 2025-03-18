from metrics.models import MetricType
from user_metrics.models import UserDefinedMetric

def metric_types(request):
    """
    Context processor to provide metrics data for templates
    """
    context = {}
    
    # Don't process for anonymous users or non-HTML responses
    if not request.user.is_authenticated:
        return {}
    
    # Get all system metrics
    system_metrics = MetricType.objects.filter(is_system=True)
    
    # Get user metrics for the current user
    user_metrics = UserDefinedMetric.objects.filter(user=request.user, is_active=True)
    user_metric_types = [um.metric_type for um in user_metrics]
    
    # Create separate lists for metrics by scope
    portfolio_metrics = []
    position_metrics = []
    transaction_metrics = []
    
    # Sort system metrics by scope
    for metric in system_metrics:
        if metric.scope_type == 'PORTFOLIO':
            portfolio_metrics.append(metric)
        elif metric.scope_type == 'POSITION':
            position_metrics.append(metric)
        elif metric.scope_type == 'TRANSACTION':
            transaction_metrics.append(metric)
    
    # Add user metrics by scope (avoid duplicates by checking IDs)
    portfolio_metric_ids = set(m.pk for m in portfolio_metrics)
    position_metric_ids = set(m.pk for m in position_metrics)
    transaction_metric_ids = set(m.pk for m in transaction_metrics)
    
    for metric in user_metric_types:
        if metric.scope_type == 'PORTFOLIO' and metric.pk not in portfolio_metric_ids:
            portfolio_metrics.append(metric)
        elif metric.scope_type == 'POSITION' and metric.pk not in position_metric_ids:
            position_metrics.append(metric)
        elif metric.scope_type == 'TRANSACTION' and metric.pk not in transaction_metric_ids:
            transaction_metrics.append(metric)
    
    # Sort each list by name for consistent display
    portfolio_metrics.sort(key=lambda x: x.name)
    position_metrics.sort(key=lambda x: x.name)
    transaction_metrics.sort(key=lambda x: x.name)
    
    context['portfolio_metrics'] = portfolio_metrics
    context['position_metrics'] = position_metrics
    context['transaction_metrics'] = transaction_metrics
    context['user_metrics'] = user_metrics
    
    return context 