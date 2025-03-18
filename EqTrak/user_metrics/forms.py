from django import forms
from .models import UserDefinedMetric
from metrics.models import MetricType, MetricValue

class UserDefinedMetricForm(forms.ModelForm):
    """Form for creating and editing user-defined metrics"""
    
    # Add fields to directly create a new MetricType
    data_type = forms.ChoiceField(
        choices=MetricType.DATA_TYPES,
        required=True,
        help_text="Select the data type for this metric (e.g., number, percentage, text/memo, etc.)"
    )
    
    scope_type = forms.ChoiceField(
        choices=MetricType.SCOPE_TYPES,
        required=True,
        help_text="Select what this metric applies to (portfolio, position, or transaction)"
    )
    
    tags = forms.CharField(
        max_length=200, 
        required=False,
        help_text="Optional: Add tags to categorize your metric (space-separated)"
    )
    
    class Meta:
        model = UserDefinedMetric
        fields = ['name', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        instance = kwargs.get('instance', None)
        
        super().__init__(*args, **kwargs)
        
        # If editing an existing metric, populate the data_type and scope_type fields
        if instance and instance.pk and instance.metric_type:
            self.fields['data_type'].initial = instance.metric_type.data_type
            self.fields['scope_type'].initial = instance.metric_type.scope_type
            self.fields['tags'].initial = instance.metric_type.tags
        
        # Add helpful descriptions
        self.fields['description'].help_text = "Describe what this metric measures or tracks"
    
    def save(self, commit=True):
        # Get or create the metric_type first
        data_type = self.cleaned_data.get('data_type')
        scope_type = self.cleaned_data.get('scope_type')
        tags = self.cleaned_data.get('tags')
        name = self.cleaned_data.get('name')
        
        instance = super().save(commit=False)
        
        # Ensure user is set
        if self.user:
            instance.user = self.user
        
        # Create a new MetricType or update existing one
        if instance.pk and instance.metric_type:
            # Update existing metric type
            metric_type = instance.metric_type
            metric_type.data_type = data_type
            metric_type.scope_type = scope_type
            metric_type.tags = tags
            # Add a user reference to the name to help differentiate
            if not metric_type.name.endswith(f" ({instance.user.username})"):
                metric_type.name = f"{name} ({instance.user.username})"
            metric_type.save()
        else:
            # Create a new MetricType with a user-specific name
            metric_type = MetricType.objects.create(
                name=f"{name} ({self.user.username})" if self.user else name,
                data_type=data_type,
                scope_type=scope_type,
                tags=tags,
                is_system=False,
                is_computed=False
            )
            instance.metric_type = metric_type
        
        if commit:
            instance.save()
        
        return instance


class UserMetricValueForm(forms.ModelForm):
    """Form for adding values to user-defined metrics"""
    
    class Meta:
        model = MetricValue
        fields = ['value', 'text_value', 'date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'text_value': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Enter your memo text here'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Optional notes about this metric value'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.metric_type = kwargs.pop('metric_type', None)
        self.user_metric = kwargs.pop('user_metric', None)
        super().__init__(*args, **kwargs)
        
        if self.metric_type:
            if self.metric_type.data_type == 'MEMO':
                self.fields['value'].widget = forms.HiddenInput()
                self.fields['text_value'].label = f"{self.metric_type.name} Content"
                self.fields['text_value'].required = True
            else:
                self.fields['text_value'].widget = forms.HiddenInput()
                self.fields['value'].label = f"{self.metric_type.name} Value"
                
                if self.metric_type.data_type == 'PERCENTAGE':
                    self.fields['value'].widget.attrs['step'] = '0.01'
                    self.fields['value'].widget.attrs['min'] = '0'
                    self.fields['value'].widget.attrs['max'] = '100'
                elif self.metric_type.data_type in ['SHARES', 'VOLUME']:
                    self.fields['value'].widget.attrs['step'] = '1'
                    self.fields['value'].widget.attrs['min'] = '0' 