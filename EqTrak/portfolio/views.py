from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Portfolio, Position, Transaction
from metrics.models import MetricType, MetricValue
from .forms import PortfolioForm, PositionForm, TransactionForm
import datetime
from itertools import groupby
from operator import attrgetter

# Create your views here.

@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user, is_active=True)
    metric_types = MetricType.objects.all().order_by('category', 'name')
    
    # Group metrics by category
    metrics_by_category = {}
    for category, metrics in groupby(metric_types, key=attrgetter('category')):
        metrics_by_category[dict(MetricType.CATEGORIES)[category]] = list(metrics)
    
    return render(request, 'portfolio/portfolio_list.html', {
        'portfolios': portfolios,
        'metrics_by_category': metrics_by_category
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
    
    # Get all metric types and separate computed from manual metrics
    metric_types = MetricType.objects.all()
    position_metrics = []
    
    for metric_type in metric_types:
        if metric_type.is_computed:
            # For computed metrics, calculate the value
            computed_value = metric_type.compute_value(position)
            metric = MetricValue(
                position=position,
                metric_type=metric_type,
                date=datetime.date.today(),
                value=computed_value,
                source='COMPUTED'
            )
            position_metrics.append(metric)
        else:
            # For manual metrics, get the most recent value
            latest_metric = MetricValue.objects.filter(
                position=position,
                metric_type=metric_type
            ).order_by('-date', '-created_at').first()
            
            if not latest_metric:
                latest_metric = MetricValue(
                    position=position,
                    metric_type=metric_type,
                    date=datetime.date.today(),
                    value=None,
                    source='USER'
                )
            position_metrics.append(latest_metric)
    
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

@login_required
def position_metrics(request, portfolio_id, position_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    
    # Get all metrics ordered by computation_order
    all_metrics = MetricType.objects.all().order_by('computation_order')
    metrics_by_type = {}
    
    for metric in all_metrics:
        if metric.is_computed:
            # Compute the value
            value = metric.compute_value(position)
            if value is not None:
                computed_value = MetricValue(
                    position=position,
                    metric_type=metric,
                    date=datetime.date.today(),
                    value=value,
                    source='COMPUTED',
                    is_forecast=False
                )
                metrics_by_type[metric] = [computed_value]
        else:
            # Get stored values
            stored_values = MetricValue.objects.filter(
                position=position,
                metric_type=metric
            ).order_by('-date')
            if stored_values.exists():
                metrics_by_type[metric] = list(stored_values)
    
    return render(request, 'portfolio/position_metrics.html', {
        'portfolio': portfolio,
        'position': position,
        'metrics_by_type': metrics_by_type
    })

@login_required
def metric_value_create(request, portfolio_id, position_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    
    if request.method == 'POST':
        form = MetricValueForm(request.POST)
        if form.is_valid():
            metric_value = form.save(commit=False)
            metric_value.position = position
            metric_value.save()
            messages.success(request, 'Metric value added successfully!')
            return redirect('portfolio:position_metrics', portfolio_id=portfolio_id, position_id=position_id)
    else:
        form = MetricValueForm()
    
    return render(request, 'portfolio/metric_value_form.html', {
        'form': form,
        'portfolio': portfolio,
        'position': position,
        'title': 'Add Metric Value',
        'submit_text': 'Add'
    })

@login_required
def metric_type_create(request):
    if request.method == 'POST':
        form = MetricTypeForm(request.POST)
        if form.is_valid():
            metric_type = form.save(commit=False)
            metric_type.is_system = False  # User-created metrics are not system metrics
            metric_type.save()
            messages.success(request, 'Metric type created successfully!')
            return redirect('portfolio:portfolio_list')
    else:
        form = MetricTypeForm()
    
    return render(request, 'portfolio/metric_type_form.html', {
        'form': form,
        'title': 'Create Metric Type',
        'submit_text': 'Create'
    })

@login_required
def metric_type_edit(request, metric_id):
    metric_type = get_object_or_404(MetricType, metric_id=metric_id)
    
    # Don't allow editing of system metrics
    if metric_type.is_system:
        messages.error(request, 'System metrics cannot be edited.')
        return redirect('portfolio:portfolio_list')
    
    if request.method == 'POST':
        form = MetricTypeForm(request.POST, instance=metric_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Metric type updated successfully!')
            return redirect('portfolio:portfolio_list')
    else:
        form = MetricTypeForm(instance=metric_type)
    
    return render(request, 'portfolio/metric_type_form.html', {
        'form': form,
        'metric_type': metric_type,
        'title': 'Edit Metric Type',
        'submit_text': 'Update'
    })

@login_required
def metric_value_edit(request, portfolio_id, position_id, value_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    metric_value = get_object_or_404(MetricValue, value_id=value_id, position=position)
    
    if request.method == 'POST':
        form = MetricValueForm(request.POST, instance=metric_value)
        if form.is_valid():
            form.save()
            messages.success(request, 'Metric value updated successfully!')
            return redirect('portfolio:position_metrics', portfolio_id=portfolio_id, position_id=position_id)
    else:
        form = MetricValueForm(instance=metric_value)
    
    return render(request, 'portfolio/metric_value_form.html', {
        'form': form,
        'portfolio': portfolio,
        'position': position,
        'metric_value': metric_value,
        'title': 'Edit Metric Value',
        'submit_text': 'Update'
    })

def metric_update(request, portfolio_id, position_id, metric_type_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id)
    position = get_object_or_404(Position, position_id=position_id)
    metric_type = get_object_or_404(MetricType, metric_id=metric_type_id)
    
    # Get the most recent metric value or create a new one
    metric = MetricValue.objects.filter(
        position=position,
        metric_type=metric_type
    ).order_by('-date').first()
    
    if request.method == 'POST':
        if metric:
            form = MetricUpdateForm(request.POST, instance=metric)
        else:
            form = MetricUpdateForm(request.POST)
        
        if form.is_valid():
            metric = form.save(commit=False)
            metric.position = position
            metric.metric_type = metric_type
            metric.date = datetime.date.today()  # Set today's date for the new value
            metric.source = 'USER'
            metric.save()
            messages.success(request, f'{metric_type.name} updated successfully.')
            return redirect('portfolio:position_detail', portfolio_id=portfolio_id, position_id=position_id)
    else:
        form = MetricUpdateForm(instance=metric)
    
    context = {
        'form': form,
        'portfolio': portfolio,
        'position': position,
        'metric_type': metric_type,
        'metric': metric,
    }
    return render(request, 'portfolio/metric_update.html', context)
