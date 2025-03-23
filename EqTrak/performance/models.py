from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class PerformanceSettings(models.Model):
    """
    Stores system-wide settings for performance calculations
    """
    updates_enabled = models.BooleanField(
        default=True,
        help_text="Enable or disable performance calculations globally"
    )
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Performance Settings')
        verbose_name_plural = _('Performance Settings')
    
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


class PerformanceMetric(models.Model):
    """
    Stores performance calculations at different levels
    """
    # Link to related objects - use generic foreign key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=40)  # Changed to CharField to support UUID primary keys
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Performance calculations
    cost_basis = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    absolute_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    percentage_gain_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    calculation_date = models.DateTimeField(auto_now=True)
    is_realized = models.BooleanField(default=False)
    status_message = models.CharField(max_length=255, blank=True, null=True, 
                                    help_text="User-friendly message explaining why metrics couldn't be calculated")
    
    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        verbose_name = _('Performance Metric')
        verbose_name_plural = _('Performance Metrics')
    
    def __str__(self):
        return f"{self.content_type.model} {self.object_id} - {self.absolute_gain_loss}"
