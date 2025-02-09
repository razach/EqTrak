from django.urls import path
from . import views

app_name = 'metrics'

urlpatterns = [
    path('create/', views.metric_type_create, name='metric_type_create'),
    path('<uuid:metric_id>/edit/', views.metric_type_edit, name='metric_type_edit'),
    path('<uuid:portfolio_id>/position/<uuid:position_id>/', 
         views.position_metrics, name='position_metrics'),
    path('<uuid:portfolio_id>/position/<uuid:position_id>/add/', 
         views.metric_value_create, name='metric_value_create'),
    path('<uuid:portfolio_id>/position/<uuid:position_id>/<uuid:value_id>/edit/', 
         views.metric_value_edit, name='metric_value_edit'),
] 