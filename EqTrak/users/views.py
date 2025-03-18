from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import UserSettings
from .forms import UserSettingsForm

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('portfolio:portfolio_list')

@login_required
def settings_view(request):
    """View for users to manage their app settings"""
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=user_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your settings have been updated.')
            return redirect('users:settings')
    else:
        form = UserSettingsForm(instance=user_settings)
    
    context = {
        'form': form,
        'page_title': 'App Settings',
    }
    return render(request, 'users/settings.html', context)

@login_required
@require_POST
def toggle_market_data(request):
    """AJAX endpoint to toggle market data setting"""
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    enabled = request.POST.get('enabled') == 'true'
    
    user_settings.market_data_enabled = enabled
    user_settings.save()
    
    return JsonResponse({
        'success': True,
        'market_data_enabled': user_settings.market_data_enabled
    })

@login_required
@require_POST
def update_market_data_provider(request):
    """AJAX endpoint to update market data provider settings"""
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    
    provider = request.POST.get('provider')
    if provider and provider in dict(UserSettings.PROVIDER_CHOICES):
        user_settings.market_data_provider = provider
        user_settings.save()
        
        return JsonResponse({
            'success': True,
            'provider': user_settings.market_data_provider,
            'provider_display': user_settings.get_market_data_provider_display()
        })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid provider selection'
    }, status=400)

@login_required
@require_POST
def update_provider_api_key(request):
    """Update API key for a specific provider"""
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    
    provider = request.POST.get('provider')
    api_key = request.POST.get('api_key', '')
    
    if provider == 'alpha_vantage':
        user_settings.alpha_vantage_api_key = api_key
        user_settings.save()
        return JsonResponse({
            'success': True,
            'message': 'Alpha Vantage API key updated successfully'
        })
    # Add more providers as needed
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid provider specified'
    }, status=400)