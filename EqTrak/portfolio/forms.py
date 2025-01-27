from django import forms
from .models import Portfolio, Position, Transaction

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'description', 'currency']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['ticker', 'position_type', 'shares', 'purchase_price']
        widgets = {
            'purchase_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'shares': forms.NumberInput(attrs={'step': '0.000001', 'class': 'form-control'}),
            'ticker': forms.TextInput(attrs={'class': 'form-control'}),
            'position_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        shares = cleaned_data.get('shares')
        purchase_price = cleaned_data.get('purchase_price')
        
        if shares and purchase_price:
            cleaned_data['cost_basis'] = shares * purchase_price
            
        return cleaned_data 

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'quantity', 'price', 'fees', 'date', 'notes']
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'step': '0.000001', 'class': 'form-control'}),
            'fees': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        } 