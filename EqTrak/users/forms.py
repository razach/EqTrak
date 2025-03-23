from django import forms
from .models import UserSettings

class UserSettingsForm(forms.ModelForm):
    """Form for editing user settings"""
    
    class Meta:
        model = UserSettings
        fields = [
            'market_data_enabled',
            'performance_enabled',
            'market_data_provider',
            'alpha_vantage_api_key',
            # Add other settings fields as needed
        ]
        widgets = {
            'alpha_vantage_api_key': forms.PasswordInput(render_value=True),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize form field appearance
        self.fields['market_data_enabled'].widget = forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'data-toggle': 'toggle',
        })
        self.fields['performance_enabled'].widget = forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'data-toggle': 'toggle',
        })
        
    def clean_alpha_vantage_api_key(self):
        """Additional validation for Alpha Vantage API key"""
        provider = self.cleaned_data.get('market_data_provider')
        api_key = self.cleaned_data.get('alpha_vantage_api_key')
        
        # If user selects Alpha Vantage but doesn't provide an API key, show a warning
        if provider == 'alpha_vantage' and not api_key:
            self.add_warning('alpha_vantage_api_key', 'Alpha Vantage requires an API key to function properly.')
        
        return api_key
    
    def add_warning(self, field, message):
        """Add a warning message to the form without preventing form submission"""
        if not hasattr(self, '_warnings'):
            self._warnings = {}
        self._warnings[field] = self._warnings.get(field, []) + [message]