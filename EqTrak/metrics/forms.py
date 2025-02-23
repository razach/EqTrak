from django import forms
from .models import MetricType, MetricValue

class MetricTypeForm(forms.ModelForm):
    class Meta:
        model = MetricType
        fields = ['name', 'scope_type', 'data_type', 'description', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={'placeholder': 'Enter comma-separated tags (e.g., Fundamental, Technical, Risk)'}),
        }

class MetricValueForm(forms.ModelForm):
    class Meta:
        model = MetricValue
        fields = ['value', 'text_value', 'date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'text_value': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Enter your memo text here'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Optional notes about this metric value'}),
        }

    def __init__(self, *args, metric_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        if metric_type:
            self.fields['value'].label = f"{metric_type.name} Value"
            if metric_type.data_type == 'MEMO':
                self.fields['value'].widget = forms.HiddenInput()
                self.fields['text_value'].label = f"{metric_type.name} Content"
                self.fields['text_value'].required = True
            else:
                self.fields['text_value'].widget = forms.HiddenInput()
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
        fields = ['date', 'value', 'text_value']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'text_value': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Enter your memo text here'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.metric_type:
            if self.instance.metric_type.data_type == 'MEMO':
                self.fields['value'].widget = forms.HiddenInput()
                self.fields['text_value'].required = True
            else:
                self.fields['text_value'].widget = forms.HiddenInput()
            if self.instance.metric_type.data_type == 'PERCENTAGE':
                self.fields['value'].widget.attrs['step'] = '0.01'
                self.fields['value'].widget.attrs['min'] = '0'
                self.fields['value'].widget.attrs['max'] = '100'
            elif self.instance.metric_type.data_type in ['SHARES', 'VOLUME']:
                self.fields['value'].widget.attrs['step'] = '1'
                self.fields['value'].widget.attrs['min'] = '0' 