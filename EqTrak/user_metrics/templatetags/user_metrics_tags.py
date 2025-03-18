from django import template
from django.urls import reverse
from user_metrics.models import UserDefinedMetric

register = template.Library()

@register.simple_tag(takes_context=True)
def is_user_defined_metric(context, metric_type):
    """Check if a metric type is user-defined for the current user"""
    if not metric_type:
        return False
    
    request = context.get('request')
    if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
        return False
    
    # Direct primary key check is more reliable than filtering on the relationship
    try:
        # More explicit and reliable query - get the PK directly
        result = UserDefinedMetric.objects.filter(
            metric_type_id=metric_type.pk,
            user=request.user,
            is_active=True
        ).exists()
        return result
    except Exception as e:
        # Add fallback error handling
        print(f"Error checking user metric: {e}")
        return False

@register.simple_tag(takes_context=True)
def get_user_metric(context, metric_type):
    """Get the user metric for the given metric type, if it exists for the current user"""
    if not metric_type:
        return None
    
    request = context.get('request')
    if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
        return None
    
    user = request.user
    try:
        return UserDefinedMetric.objects.get(metric_type=metric_type, user=user, is_active=True)
    except UserDefinedMetric.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error getting user metric: {e}")
        return None

@register.simple_tag
def get_add_value_url(user_metric, portfolio, position=None, transaction=None):
    """Generate the URL for adding a value to a user-defined metric"""
    if not user_metric or not portfolio:
        return "#"
    
    url = f"/user-metrics/{user_metric.pk}/add-value/portfolio/{portfolio.portfolio_id}/"
    
    if position:
        url += f"position/{position.position_id}/"
        
        if transaction:
            url += f"transaction/{transaction.transaction_id}/"
    
    return url 