from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Portfolio, Position, Transaction
from .forms import PortfolioForm, PositionForm, TransactionForm
import datetime
from itertools import groupby
from operator import attrgetter
from metrics.views import get_position_metrics
from metrics.models import MetricType, MetricValue

# Create your views here.

@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user, is_active=True)
    return render(request, 'portfolio/portfolio_list.html', {
        'portfolios': portfolios
    })

@login_required
def portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            messages.success(request, 'Portfolio created successfully!')
            return redirect('portfolio:portfolio_list')
    else:
        form = PortfolioForm()
    
    return render(request, 'portfolio/portfolio_form.html', {
        'form': form,
        'title': 'Create Portfolio',
        'submit_text': 'Create'
    })

def home(request):
    if request.user.is_authenticated:
        return redirect('portfolio:portfolio_list')
    return render(request, 'home.html')

def custom_logout(request):
    logout(request)
    return redirect('home')

def portfolio_detail(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id)
    positions = portfolio.position_set.filter(is_active=True)  # Get active positions
    return render(request, 'portfolio/portfolio_detail.html', {
        'portfolio': portfolio,
        'positions': positions
    })

@login_required
def position_create(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.portfolio = portfolio
            position.save()
            
            # Create initial transaction if initial shares and price are provided
            initial_shares = request.POST.get('initial_shares')
            initial_price = request.POST.get('initial_price')
            initial_date = request.POST.get('initial_date')
            market_price = request.POST.get('market_price')
            market_date = request.POST.get('market_date')
            
            if initial_shares and initial_price:
                Transaction.objects.create(
                    position=position,
                    transaction_type='BUY',
                    quantity=initial_shares,
                    price=initial_price,
                    date=initial_date or datetime.date.today(),  # Fallback to today if no date provided
                    status='COMPLETED',
                    currency=portfolio.currency
                )
            
            # Create market price metric if provided
            if market_price and market_date:
                market_price_metric = MetricType.objects.get(
                    name='Market Price',
                    is_system=True
                )
                MetricValue.objects.create(
                    position=position,
                    metric_type=market_price_metric,
                    date=market_date,
                    value=market_price,
                    source='USER'
                )
            
            messages.success(request, 'Position created successfully!')
            return redirect('portfolio:portfolio_detail', portfolio_id=portfolio_id)
    else:
        form = PositionForm()
    
    return render(request, 'portfolio/position_form.html', {
        'form': form,
        'portfolio': portfolio,
        'title': 'Add Position',
        'submit_text': 'Add',
        'today': datetime.date.today()  # Add today's date for the default value
    })

@login_required
def position_delete(request, portfolio_id, position_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    
    if request.method == 'POST':
        # Soft delete all related transactions
        position.transaction_set.all().update(status='CANCELLED')
        
        # Soft delete the position
        position.is_active = False
        position.shares = 0
        position.cost_basis = 0
        position.purchase_price = 0
        position.save()
        
        messages.success(request, 'Position and related transactions deleted successfully!')
        return redirect('portfolio:portfolio_detail', portfolio_id=portfolio_id)
    
    return render(request, 'portfolio/position_confirm_delete.html', {
        'portfolio': portfolio,
        'position': position,
        'transaction_count': position.transaction_set.count()
    })

@login_required
def position_detail(request, portfolio_id, position_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    transactions = position.transaction_set.all().order_by('-date', '-created_at')
    position_metrics = get_position_metrics(position)
    
    return render(request, 'portfolio/position_detail.html', {
        'portfolio': portfolio,
        'position': position,
        'transactions': transactions,
        'position_metrics': position_metrics
    })

@login_required
def transaction_create(request, portfolio_id, position_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.position = position
            transaction.status = 'COMPLETED'
            transaction.currency = portfolio.currency
            transaction.save()
            
            messages.success(request, 'Transaction added successfully!')
            return redirect('portfolio:position_detail', portfolio_id=portfolio_id, position_id=position_id)
    else:
        initial_data = {
            'date': datetime.date.today(),
            'transaction_type': request.GET.get('type', 'BUY')
        }
        form = TransactionForm(initial=initial_data)
    
    return render(request, 'portfolio/transaction_form.html', {
        'form': form,
        'portfolio': portfolio,
        'position': position,
        'title': f'Add {dict(Transaction.TRANSACTION_TYPES).get(initial_data["transaction_type"], "New")} Transaction',
        'submit_text': 'Add'
    })
