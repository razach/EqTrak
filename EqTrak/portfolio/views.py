from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from .models import Portfolio, Position, Transaction
from .forms import PortfolioForm, PositionForm, TransactionForm
import datetime
from itertools import groupby
from operator import attrgetter
from metrics.views import get_position_metrics, get_portfolio_metrics
from metrics.models import MetricType, MetricValue
from market_data.services import MarketDataService
from market_data.models import MarketDataSettings

# Create your views here.

@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user, is_active=True)
    # Get system metrics for portfolios
    portfolio_metrics = MetricType.objects.filter(
        scope_type='PORTFOLIO',
        is_system=True,
        data_type__in=['CURRENCY', 'PERCENTAGE']  # Only show currency and percentage metrics
    ).exclude(data_type='MEMO').order_by('computation_order', 'name')
    
    # Get market data update settings
    market_data_updates_enabled = MarketDataSettings.is_updates_enabled()
    
    return render(request, 'portfolio/portfolio_list.html', {
        'portfolios': portfolios,
        'portfolio_metrics': portfolio_metrics,
        'market_data_updates_enabled': market_data_updates_enabled
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

@login_required
def portfolio_detail(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    positions = portfolio.position_set.filter(is_active=True)  # Get active positions
    portfolio_metrics = get_portfolio_metrics(portfolio)  # Get portfolio metrics
    position_metrics = Position.get_display_metrics()  # Get position system metrics
    
    return render(request, 'portfolio/portfolio_detail.html', {
        'portfolio': portfolio,
        'positions': positions,
        'portfolio_metrics': portfolio_metrics,
        'position_metrics': position_metrics
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
    
    # Check if market data updates are enabled
    market_data_updates_enabled = MarketDataSettings.is_updates_enabled()
    
    # Only sync market data if updates are enabled
    if market_data_updates_enabled:
        try:
            MarketDataService.sync_price_with_metrics(position)
        except Exception as e:
            messages.warning(request, f"Could not update market data: {str(e)}")
    else:
        messages.info(request, "Market data updates are currently disabled.")
    
    # Get position metrics (which now includes the updated market price)
    position_metrics = get_position_metrics(position)
    
    # Get the price staleness info
    is_stale = False
    try:
        latest_price = MarketDataService.get_latest_price(position.security)
        is_stale = latest_price.get('is_stale', False)
    except Exception:
        is_stale = True
    
    context = {
        'portfolio': portfolio,
        'position': position,
        'transactions': transactions,
        'position_metrics': position_metrics,
        'is_stale': is_stale
    }
    
    return render(request, 'portfolio/position_detail.html', context)

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

@login_required
def transaction_edit(request, portfolio_id, position_id, transaction_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, position=position)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.position = position  # Ensure position is set
            transaction.currency = portfolio.currency  # Ensure currency matches portfolio
            transaction.save()
            
            messages.success(request, 'Transaction updated successfully!')
            return redirect('portfolio:position_detail', portfolio_id=portfolio_id, position_id=position_id)
    else:
        form = TransactionForm(instance=transaction)
    
    return render(request, 'portfolio/transaction_form.html', {
        'form': form,
        'portfolio': portfolio,
        'position': position,
        'transaction': transaction,
        'title': f'Edit {transaction.get_transaction_type_display()} Transaction',
        'submit_text': 'Update'
    })

@login_required
def toggle_market_data_updates(request):
    if request.method == 'POST':
        enabled = request.POST.get('enabled') == 'true'
        MarketDataSettings.set_updates_enabled(enabled)
        
        # Clear existing messages to prevent multiple banners
        storage = messages.get_messages(request)
        for _ in storage:
            # Iterating through messages marks them as read
            pass
            
        messages.success(request, f"Market data updates {'enabled' if enabled else 'disabled'} successfully!")
        return JsonResponse({'success': True, 'enabled': enabled})
    return JsonResponse({'success': False}, status=400)
