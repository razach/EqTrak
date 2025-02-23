from .views import metric_types_list

def metric_types(request):
    # Only provide metrics data for authenticated users
    if request.user.is_authenticated:
        return metric_types_list(request)
    return {'metrics_by_category': {}} 