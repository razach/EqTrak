"""
URL configuration for EqTrak project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from portfolio.views import home, custom_logout
from users.views import SignUpView

# Add a root URL pattern to redirect to portfolio
urlpatterns = [
    path('', home, name='home'),  # Redirect root to portfolio
    path('admin/', admin.site.urls),
    path('accounts/logout/', custom_logout, name='logout'),  # Use our custom logout view
    path('accounts/', include('django.contrib.auth.urls')),  # Other auth URLs
    path('portfolio/', include('portfolio.urls')),  # We'll create this next
    path('signup/', SignUpView.as_view(), name='signup'),
]
