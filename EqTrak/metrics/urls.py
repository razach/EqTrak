from django.urls import path
from . import views

app_name = 'metrics'

urlpatterns = [
    path('create/', views.metric_type_create, name='metric_type_create'),
    path('<uuid:metric_id>/edit/', views.metric_type_edit, name='metric_type_edit'),
    path('<uuid:portfolio_id>/', views.portfolio_metrics, name='portfolio_metrics'),
    # Portfolio-level metric value create
    path('<uuid:portfolio_id>/add/', 
         views.metric_value_create, name='portfolio_metric_value_create'),
    path('<uuid:portfolio_id>/position/<uuid:position_id>/', 
         views.position_metrics, name='position_metrics'),
    path('<uuid:portfolio_id>/position/<uuid:position_id>/add/', 
         views.metric_value_create, name='metric_value_create'),
    path('<uuid:portfolio_id>/position/<uuid:position_id>/<uuid:value_id>/edit/', 
         views.metric_value_edit, name='metric_value_edit'),
    path('<uuid:portfolio_id>/position/<uuid:position_id>/metric/<uuid:metric_type_id>/update/',
         views.metric_update, name='metric_update'),
    # Portfolio-level metric history
    path('<uuid:portfolio_id>/metric/<uuid:metric_id>/history/',
         views.metric_history, name='metric_history'),
    # Position-level metric history
    path('<uuid:portfolio_id>/position/<uuid:position_id>/metric/<uuid:metric_id>/history/',
         views.metric_history, name='position_metric_history'),
    path('<uuid:portfolio_id>/position/<uuid:position_id>/transaction/<uuid:transaction_id>/',
         views.transaction_metrics, name='transaction_metrics'),
    # Add a new URL pattern for portfolio-level metric value editing
    path('<uuid:portfolio_id>/<uuid:value_id>/edit/', views.metric_value_edit, name='metric_value_edit'),
] 