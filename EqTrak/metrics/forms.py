from django import forms
from .models import MetricType, MetricValue

class MetricTypeForm(forms.ModelForm):
    class Meta:
        model = MetricType
        fields = ['name', 'category', 'data_type', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class MetricValueForm(forms.ModelForm):
    class Meta:
        model = MetricValue
        fields = ['value', 'date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Optional notes about this metric value'}),
        }

    def __init__(self, *args, metric_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        if metric_type:
            self.fields['value'].label = f"{metric_type.name} Value"
            if metric_type.data_type == 'PERCENTAGE':
                self.fields['value'].widget.attrs['step'] = '0.01'
                self.fields['value'].widget.attrs['min'] = '0'
                self.fields['value'].widget.attrs['max'] = '100'
            elif metric_type.data_type in ['SHARES', 'VOLUME']:
                self.fields['value'].widget.attrs['step'] = '1'
                self.fields['value'].widget.attrs['min'] = '0'

class MetricUpdateForm(forms.ModelForm):
    class Meta:
        model = MetricValue
        fields = ['date', 'value']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'})
        } 