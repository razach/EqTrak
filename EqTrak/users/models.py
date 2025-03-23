from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .fields import EncryptedCharField

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
    
    # Performance module toggle
    performance_enabled = models.BooleanField(
        default=True,
        verbose_name="Enable Performance Tracking",
        help_text="Enable or disable performance tracking and gain/loss calculations"
    )
    
    # Market data provider preference
    PROVIDER_CHOICES = [
        ('system', 'System Default'),
        ('yahoo', 'Yahoo Finance'),
        ('alpha_vantage', 'Alpha Vantage'),
        # Add more providers as they become available
    ]
    
    market_data_provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='system',
        verbose_name="Market Data Provider",
        help_text="Select which market data provider to use"
    )
    
    # API Keys for providers that require authentication (encrypted)
    alpha_vantage_api_key = EncryptedCharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Alpha Vantage API Key"
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
