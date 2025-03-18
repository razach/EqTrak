from django.conf import settings

def user_metrics_enabled(request):
    """
    Adds a variable to the context to check if the user_metrics app is enabled
    """
    return {
        'user_metrics_enabled': 'user_metrics' in settings.INSTALLED_APPS
    } 