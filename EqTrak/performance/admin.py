from django.contrib import admin
from .models import PerformanceSettings, PerformanceMetric

@admin.register(PerformanceSettings)
class PerformanceSettingsAdmin(admin.ModelAdmin):
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

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'content_type', 'object_id', 'cost_basis', 
        'current_value', 'absolute_gain_loss', 'percentage_gain_loss', 
        'calculation_date', 'is_realized'
    ]
    list_filter = ['content_type', 'is_realized', 'calculation_date']
    readonly_fields = ['calculation_date']
    search_fields = ['object_id']
