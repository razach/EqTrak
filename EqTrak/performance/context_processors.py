from django.conf import settings

def performance_settings(request):
    """
    Adds performance-related configuration to the template context.
    """
    return {
        'INSTALLED_APPS': settings.INSTALLED_APPS,
        'performance_enabled': 'performance' in settings.INSTALLED_APPS
    } 