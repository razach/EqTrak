from .views import get_metrics_by_type

def metric_types(request):
    # Only provide metrics data for authenticated users
    if request.user.is_authenticated:
        return {'metrics_by_type': get_metrics_by_type()}
    return {'metrics_by_type': {}} 