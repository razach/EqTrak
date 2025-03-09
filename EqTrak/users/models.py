from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserSettings(models.Model):
    """
    Stores user-specific settings and app toggle preferences
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    
    # App toggle preferences
    market_data_enabled = models.BooleanField(
        default=True,
        verbose_name="Enable Market Data",
        help_text="Enable or disable market data updates for your account"
    )
    
    # Add other app toggles as needed
    # metrics_app_enabled = models.BooleanField(default=True)
    # user_defined_metrics_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"
    
    def __str__(self):
        return f"{self.user.username}'s Settings"

# Signal to create user settings when a new user is created
@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_settings(sender, instance, **kwargs):
    if not hasattr(instance, 'settings'):
        UserSettings.objects.create(user=instance)
    else:
        instance.settings.save()
