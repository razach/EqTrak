from django.contrib import admin
from .models import UserSettings

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'market_data_enabled', 'created_at', 'updated_at']
    list_filter = ['market_data_enabled']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
