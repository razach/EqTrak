from django.contrib import admin
from .models import UserDefinedMetric

@admin.register(UserDefinedMetric)
class UserDefinedMetricAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'metric_type', 'is_active', 'created_at')
    list_filter = ('is_active', 'metric_type', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'user', 'is_active')
        }),
        ('Metric Details', {
            'fields': ('metric_type', 'latest_value')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    ) 