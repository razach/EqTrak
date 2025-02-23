from django.contrib import admin
from .models import MetricType, MetricValue

@admin.register(MetricType)
class MetricTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'scope_type', 'data_type', 'is_system', 'is_computed', 'computation_order')
    list_filter = ('scope_type', 'data_type', 'is_system', 'is_computed')
    search_fields = ('name', 'description', 'tags')
    readonly_fields = ('metric_id',)

@admin.register(MetricValue)
class MetricValueAdmin(admin.ModelAdmin):
    list_display = ('metric_type', 'date', 'value', 'source', 'is_forecast', 'created_at')
    list_filter = ('metric_type__scope_type', 'source', 'is_forecast', 'scenario')
    search_fields = ('metric_type__name', 'notes')
    readonly_fields = ('value_id', 'created_at', 'updated_at')
    date_hierarchy = 'date'
