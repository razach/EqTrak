from django.urls import path
from . import views

app_name = 'user_metrics'

urlpatterns = [
    path('', views.user_metric_list, name='list'),
    path('create/', views.create_user_metric, name='create'),
    path('<int:pk>/edit/', views.edit_user_metric, name='edit'),
    path('<int:pk>/delete/', views.delete_user_metric, name='delete'),
    path('<int:metric_id>/add-value/portfolio/<uuid:portfolio_id>/', 
         views.add_metric_value, name='add_portfolio_value'),
    path('<int:metric_id>/add-value/portfolio/<uuid:portfolio_id>/position/<uuid:position_id>/', 
         views.add_metric_value, name='add_position_value'),
    path('<int:metric_id>/add-value/portfolio/<uuid:portfolio_id>/position/<uuid:position_id>/transaction/<uuid:transaction_id>/', 
         views.add_metric_value, name='add_transaction_value'),
] 