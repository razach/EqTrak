from django.contrib import admin
from .models import Security, PriceData, MarketDataSettings

@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'security_type', 'exchange', 'currency', 'active')
    list_filter = ('security_type', 'exchange', 'currency', 'active')
    search_fields = ('symbol', 'name')
    ordering = ('symbol',)

@admin.register(PriceData)
class PriceDataAdmin(admin.ModelAdmin):
    list_display = ('security', 'date', 'open', 'high', 'low', 'close', 'volume')
    list_filter = ('date', 'security__security_type')
    search_fields = ('security__symbol', 'security__name')
    date_hierarchy = 'date'
    ordering = ('-date',)

@admin.register(MarketDataSettings)
class MarketDataSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'updates_enabled', 'last_modified']
    list_editable = ['updates_enabled']
    readonly_fields = ['last_modified']
    
    def has_add_permission(self, request):
        # Prevent creating additional settings objects (singleton model)
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the settings object
        return False
