from django.urls import path
from . import views

app_name = 'performance'

urlpatterns = [
    # Main performance dashboard
    path('', views.performance_dashboard, name='dashboard'),
    
    # Portfolio performance
    path('portfolio/<uuid:portfolio_id>/', views.portfolio_performance, name='portfolio'),
    
    # Position performance
    path('portfolio/<uuid:portfolio_id>/position/<uuid:position_id>/', 
         views.position_performance, name='position'),
    
    # Transaction performance
    path('portfolio/<uuid:portfolio_id>/position/<uuid:position_id>/transaction/<uuid:transaction_id>/', 
         views.transaction_performance, name='transaction'),
    
    # Recalculate all metrics
    path('recalculate/', views.recalculate_all, name='recalculate'),
    
    # API endpoints
    path('api/position/<uuid:position_id>/', views.api_position_performance, name='api_position'),
] 