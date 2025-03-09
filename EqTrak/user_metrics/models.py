from django.db import models
from django.conf import settings
from metrics.models import MetricType, MetricValue

class UserDefinedMetric(models.Model):
    """Model for user-defined custom metrics"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_metrics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metric_type = models.ForeignKey(MetricType, on_delete=models.CASCADE, related_name='user_defined_metrics')
    is_active = models.BooleanField(default=True)
    
    # Associated metric value - the latest value calculated for this metric
    latest_value = models.OneToOneField(
        MetricValue, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='user_defined_metric'
    )
    
    def __str__(self):
        return f"{self.name} (by {self.user.username})"
    
    class Meta:
        verbose_name = "User Defined Metric"
        verbose_name_plural = "User Defined Metrics"
        ordering = ['-created_at']
        # Add index for performance
        indexes = [
            models.Index(fields=['user', 'metric_type']),
            models.Index(fields=['is_active']),
        ] 