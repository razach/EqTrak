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
        fields = ['ticker', 'position_type']
        widgets = {
            'ticker': forms.TextInput(attrs={'class': 'form-control'}),
            'position_type': forms.Select(attrs={'class': 'form-control'}),
        }

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