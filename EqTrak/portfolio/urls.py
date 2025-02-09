from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.portfolio_list, name='portfolio_list'),
    path('create/', views.portfolio_create, name='portfolio_create'),
    path('<uuid:portfolio_id>/', views.portfolio_detail, name='portfolio_detail'),
    path('<uuid:portfolio_id>/position/add/', views.position_create, name='position_create'),
    path('<uuid:portfolio_id>/position/<uuid:position_id>/delete/', views.position_delete, name='position_delete'),
    path('<uuid:portfolio_id>/position/<uuid:position_id>/', views.position_detail, name='position_detail'),
    path('<uuid:portfolio_id>/position/<uuid:position_id>/transaction/add/', views.transaction_create, name='transaction_create'),
] 