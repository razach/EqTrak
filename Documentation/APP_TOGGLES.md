# App Toggles - Implementation Guide

This document explains how to implement the app toggle pattern for new Django app modules in EqTrak. This pattern allows:

1. Admin-level system-wide control of features
2. User-specific preferences for enabling/disabling features
3. Clear visual indication of feature status
4. User-specific provider selections and API key management

## Architecture Overview

The app toggle pattern consists of these main components:

1. **System-wide Settings**: Managed by admin, can disable features site-wide
2. **User-specific Settings**: Allow users to toggle features and select providers according to their preferences
3. **Access Control Logic**: Checks both system and user settings when accessing features
4. **Provider Factory**: Selects the appropriate service provider based on user preferences

## Implementation Steps for New App Modules

Follow these steps to add the toggle pattern to your new Django app:

### 1. Create System-wide Settings Model

Create a singleton model for system-wide settings in your app's `models.py`:

```python
class YourAppSettings(models.Model):
    """
    Stores system-wide settings for your app features
    """
    updates_enabled = models.BooleanField(
        default=True,
        help_text="Enable or disable your app feature globally"
    )
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Your App Settings')
        verbose_name_plural = _('Your App Settings')
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton settings instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    @classmethod
    def is_feature_enabled(cls):
        """Check if the feature is enabled"""
        return cls.get_instance().updates_enabled
    
    @classmethod
    def set_feature_enabled(cls, enabled):
        """Set the feature enabled state"""
        instance = cls.get_instance()
        instance.updates_enabled = enabled
        instance.save()
        return instance
```

### 2. Register the Settings Model in Admin

In your app's `admin.py`:

```python
@admin.register(YourAppSettings)
class YourAppSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'updates_enabled', 'last_modified']
    list_editable = ['updates_enabled']
    readonly_fields = ['last_modified']
    
    def has_add_permission(self, request):
        # Prevent creating additional settings objects
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the settings object
        return False
```

### 3. Add User-specific Toggle to UserSettings Model

Update the `UserSettings` model in the users app by adding a field for your feature:

```python
# In users/models.py
class UserSettings(models.Model):
    # Existing fields...
    
    # Add your app toggle here
    your_app_feature_enabled = models.BooleanField(
        default=True,
        verbose_name="Enable Your Feature",
        help_text="Enable or disable your feature for your account"
    )
    
    # If your feature uses providers, add provider selection
    YOUR_PROVIDER_CHOICES = [
        ('system', 'System Default'),
        ('provider1', 'Provider 1'),
        ('provider2', 'Provider 2'),
    ]
    
    your_feature_provider = models.CharField(
        max_length=20,
        choices=YOUR_PROVIDER_CHOICES,
        default='system',
        verbose_name="Your Feature Provider",
        help_text="Select which provider to use for your feature"
    )
    
    # If your providers need API keys, use EncryptedCharField
    provider1_api_key = EncryptedCharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Provider 1 API Key"
    )
```

Don't forget to create and apply migrations:

```bash
python manage.py makemigrations users
python manage.py migrate
```

### 4. Update the User Settings Form

Add your new field to the form in `users/forms.py`:

```python
class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            'market_data_enabled',
            'your_app_feature_enabled',
            # Other fields...
        ]
```

### 5. Create an Access Control Decorator

Create a decorator in your app to check permissions:

```python
def check_feature_access(func):
    """
    Decorator to check if access to your feature is enabled.
    Checks both system-wide settings and user-specific settings.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Find user parameter
        user = kwargs.get('user')
        
        # Extract from positional args if not in kwargs
        if user is None and len(args) > 1:
            # Find the parameter index (details similar to market_data)
            pass
        
        # Check system-wide setting first
        if not YourAppSettings.is_feature_enabled():
            logger.info("Feature disabled at system level")
            return get_appropriate_fallback_value()
            
        # If no user, system setting is sufficient
        if user is None:
            return func(*args, **kwargs)
            
        # Check user-specific setting
        try:
            if not user.settings.your_app_feature_enabled:
                logger.info(f"Feature disabled for user {user.username}")
                return get_appropriate_fallback_value()
        except (AttributeError, Exception):
            # If user settings don't exist, default to enabled
            pass
            
        # Feature access allowed, call the function
        return func(*args, **kwargs)
        
    return wrapper
```

### 6. Create a Service Layer with Provider Factory

Implement a service layer with the decorator applied to methods, and use a provider factory:

```python
class YourProviderFactory:
    """Factory for creating your feature providers."""
    
    @staticmethod
    def get_provider(user=None):
        """
        Get the provider based on system settings and user preferences.
        
        Args:
            user: Optional user to consider provider preferences for
            
        Returns:
            An instance of the appropriate provider.
        """
        # Default to system setting
        provider_name = getattr(settings, 'YOUR_FEATURE_PROVIDER', 'default_provider')
        
        # If user is provided, check for user preference
        if user is not None and hasattr(user, 'settings'):
            if user.settings.your_feature_provider != 'system':
                provider_name = user.settings.your_feature_provider
        
        if provider_name == 'provider1':
            provider = Provider1()
            # If user has a custom API key, use it
            if user and hasattr(user, 'settings') and user.settings.provider1_api_key:
                provider.api_key = user.settings.provider1_api_key
            return provider
        elif provider_name == 'provider2':
            return Provider2()
            
        # Add more providers as needed
        
        # Default provider
        return DefaultProvider()

class YourAppService:
    """Service for interacting with your feature"""
    
    @staticmethod
    def is_feature_enabled(user=None):
        """
        Check if the feature is enabled for the given user.
        System settings override user preferences.
        """
        # System setting takes precedence
        if not YourAppSettings.is_feature_enabled():
            return False
            
        # If no user, return system setting
        if user is None:
            return True
            
        # Check user setting
        try:
            return user.settings.your_app_feature_enabled
        except (AttributeError, Exception):
            return True
    
    @staticmethod
    @check_feature_access
    def your_feature_method(param1, param2, user=None):
        """
        Implement your feature method using the appropriate provider.
        Access control will be handled by the decorator.
        """
        provider = YourProviderFactory.get_provider(user)
        return provider.do_something(param1, param2)
```

### 7. Update the App Toggle Status Template

Update the `app_toggles_status.html` template to include your feature:

```html
<!-- In templates/users/components/app_toggles_status.html -->

<!-- Add this inside the existing rows div -->
<div class="col-md-6 col-lg-4 mb-3">
    <div class="d-flex align-items-center">
        <div class="me-3">
            {% load your_app_tags %}
            {% get_your_app_system_setting as system_feature_enabled %}
            
            {% if not system_feature_enabled %}
                <span class="badge bg-danger rounded-pill" title="Disabled by administrator">
                    <i class="bi bi-slash-circle-fill"></i>
                </span>
            {% elif user.settings.your_app_feature_enabled %}
                <span class="badge bg-success rounded-pill">
                    <i class="bi bi-check-circle-fill"></i>
                </span>
            {% else %}
                <span class="badge bg-secondary rounded-pill">
                    <i class="bi bi-x-circle-fill"></i>
                </span>
            {% endif %}
        </div>
        <div>
            <h6 class="mb-0">Your Feature</h6>
            <small class="text-muted">
                {% if not system_feature_enabled %}
                    <span class="text-danger">Feature disabled by administrator</span>
                {% elif user.settings.your_app_feature_enabled %}
                    Feature enabled
                {% else %}
                    Feature disabled
                {% endif %}
            </small>
            
            {% if not system_feature_enabled and user.settings.your_app_feature_enabled %}
            <div class="mt-1">
                <small class="text-muted fst-italic">
                    Your preference: Enabled, but overridden by system settings
                </small>
            </div>
            {% endif %}
        </div>
    </div>
</div>
```

### 8. Create Template Tags

Create template tags to access your system settings:

```python
# In your_app/templatetags/your_app_tags.py
from django import template
from your_app.models import YourAppSettings

register = template.Library()

@register.simple_tag
def get_your_app_system_setting():
    """Returns the system-wide feature enabled setting."""
    return YourAppSettings.is_feature_enabled()
```

## Best Practices

1. **Always check both settings**: System settings should always override user preferences
2. **Use decorators**: Apply the access check decorator to all methods that use the feature
3. **Consistent fallback behavior**: Define what should happen when access is denied
4. **Clear UI feedback**: Always show users when their preferences are being overridden
5. **Context-aware checks**: Pass the user context through to all service methods

## Example Usage in Views

When using your feature in views:

```python
@login_required
def your_view(request):
    # Pass user context to service methods
    result = YourAppService.your_feature_method(param1, param2, user=request.user)
    
    # Rest of your view code
    return render(request, 'your_template.html', {'result': result})
```

## Example Usage in Tasks/Scheduled Jobs

For background tasks or management commands:

```python
def your_scheduled_task():
    # For system-wide tasks, pass user=None
    YourAppService.your_feature_method(param1, param2, user=None)
```