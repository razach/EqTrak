from django import forms
from .models import UserSettings

class UserSettingsForm(forms.ModelForm):
    """Form for managing user app settings"""
    
    class Meta:
        model = UserSettings
        fields = ['market_data_enabled']
        # Add more fields as app toggles are added
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize form field appearance
        self.fields['market_data_enabled'].widget = forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'data-toggle': 'toggle',
        }) 