from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('settings/', views.settings_view, name='settings'),
    path('settings/toggle-market-data/', views.toggle_market_data, name='toggle_market_data'),
    path('update-provider/', views.update_market_data_provider, name='update_provider'),
    path('update-api-key/', views.update_provider_api_key, name='update_api_key'),
]