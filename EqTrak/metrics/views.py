from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from portfolio.models import Portfolio, Position, Transaction
from .models import MetricType, MetricValue
from .forms import MetricTypeForm, MetricValueForm, MetricUpdateForm
import datetime
from itertools import groupby
from operator import attrgetter
from django.http import Http404

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
    
    return render(request, 'metrics/metric_type_form.html', {
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
    
    return render(request, 'metrics/metric_type_form.html', {
        'form': form,
        'metric_type': metric_type,
        'title': 'Edit Metric Type',
        'submit_text': 'Update'
    })

@login_required
def position_metrics(request, portfolio_id, position_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    
    # Get position-scoped metrics ordered by computation_order
    all_metrics = MetricType.objects.filter(scope_type='POSITION').order_by('computation_order', 'name')
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
            
            # Always include the metric, even if it has no values
            if stored_values.exists():
                metrics_by_type[metric] = list(stored_values)
            else:
                # Create an empty metric value to show the metric in the list
                empty_value = MetricValue(
                    position=position,
                    metric_type=metric,
                    date=datetime.date.today(),
                    source='USER'
                )
                metrics_by_type[metric] = [empty_value]
    
    return render(request, 'metrics/position_metrics.html', {
        'portfolio': portfolio,
        'position': position,
        'metrics_by_type': metrics_by_type
    })

@login_required
def metric_value_create(request, portfolio_id, position_id=None):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = None
    if position_id:
        position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    
    # Get the metric type from query parameters
    metric_type_id = request.GET.get('metric_type')
    if not metric_type_id:
        messages.error(request, 'No metric type specified.')
        if position and position_id:  # Ensure position_id is not None
            return redirect('metrics:position_metrics', portfolio_id=portfolio_id, position_id=position_id)
        else:
            return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
    
    metric_type = get_object_or_404(MetricType, metric_id=metric_type_id)
    
    # Validate that the metric type matches the expected scope
    if metric_type.scope_type == 'PORTFOLIO' and position_id:
        messages.warning(request, f'{metric_type.name} is a portfolio-level metric and should be added at the portfolio level.')
        return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
    elif metric_type.scope_type == 'POSITION' and not position_id:
        messages.warning(request, f'{metric_type.name} is a position-level metric and requires a position.')
        return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
    elif metric_type.scope_type == 'TRANSACTION' and not position_id:
        messages.warning(request, f'{metric_type.name} is a transaction-level metric and requires a position and transaction.')
        return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
    
    # For transaction metrics, get the transaction
    transaction = None
    if metric_type.scope_type == 'TRANSACTION':
        transaction_id = request.GET.get('transaction_id')
        if not transaction_id:
            messages.error(request, 'No transaction specified for transaction metric.')
            if position_id:  # Ensure position_id is not None
                return redirect('metrics:position_metrics', portfolio_id=portfolio_id, position_id=position_id)
            else:
                return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id, position=position)
    
    if request.method == 'POST':
        form = MetricValueForm(request.POST, metric_type=metric_type)
        if form.is_valid():
            metric_value = form.save(commit=False)
            # Set the appropriate object based on scope type - only set one target
            if metric_type.scope_type == 'TRANSACTION':
                if not transaction:
                    messages.error(request, 'Cannot add transaction metrics without a transaction.')
                    return redirect('metrics:position_metrics', portfolio_id=portfolio_id, position_id=position_id)
                metric_value.transaction = transaction
                # Clear any other target fields
                metric_value.position = None
                metric_value.portfolio = None
            elif metric_type.scope_type == 'POSITION':
                if not position:
                    messages.error(request, 'Cannot add position metrics without a position.')
                    return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
                metric_value.position = position
                # Clear any other target fields
                metric_value.portfolio = None
                metric_value.transaction = None
            else:  # PORTFOLIO scope
                metric_value.portfolio = portfolio
                # Clear any other target fields
                metric_value.position = None
                metric_value.transaction = None
            
            metric_value.metric_type = metric_type
            metric_value.source = 'USER'
            metric_value.save()
            messages.success(request, f'{metric_type.name} value added successfully!')
            
            # Redirect based on scope type
            if metric_type.scope_type == 'TRANSACTION':
                if position_id:  # Ensure position_id is not None
                    return redirect('metrics:transaction_metrics', 
                                  portfolio_id=portfolio_id, 
                                  position_id=position_id,
                                  transaction_id=transaction.transaction_id)
                else:
                    return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
            elif metric_type.scope_type == 'POSITION':
                if position and position_id:  # Ensure position_id is not None
                    return redirect('metrics:position_metrics', 
                                  portfolio_id=portfolio_id, 
                                  position_id=position_id)
                else:
                    return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
            else:  # PORTFOLIO scope
                return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
    else:
        form = MetricValueForm(
            metric_type=metric_type,
            initial={'date': datetime.date.today()}
        )
    
    context = {
        'form': form,
        'portfolio': portfolio,
        'metric_type': metric_type,
        'title': f'Add {metric_type.name} Value',
        'submit_text': 'Add'
    }
    
    if position:
        context['position'] = position
    if transaction:
        context['transaction'] = transaction
    
    return render(request, 'metrics/metric_value_form.html', context)

@login_required
def metric_value_edit(request, portfolio_id, position_id=None, value_id=None):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = None
    if position_id:
        position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    
    # Get the metric value based on scope
    transaction = None
    if position:
        # Try to get the metric value for position or transaction scope
        try:
            metric_value = get_object_or_404(MetricValue, value_id=value_id, position=position)
        except:
            # Maybe it's a transaction-level metric
            metric_value = get_object_or_404(MetricValue, value_id=value_id)
            if metric_value.transaction and metric_value.transaction.position == position:
                transaction = metric_value.transaction
            else:
                # Not found or not related to this position
                raise Http404("Metric value not found")
    else:
        # Looking for a portfolio-level metric
        metric_value = get_object_or_404(MetricValue, value_id=value_id, portfolio=portfolio)
    
    # Validate that the metric type matches the expected scope
    if metric_value.metric_type.scope_type == 'PORTFOLIO' and position_id:
        messages.warning(request, f'{metric_value.metric_type.name} is a portfolio-level metric and should be edited at the portfolio level.')
        return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
    elif metric_value.metric_type.scope_type == 'POSITION' and not position_id:
        messages.warning(request, f'{metric_value.metric_type.name} is a position-level metric and requires a position.')
        return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
    elif metric_value.metric_type.scope_type == 'TRANSACTION' and not position_id:
        messages.warning(request, f'{metric_value.metric_type.name} is a transaction-level metric and requires a position and transaction.')
        return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
    
    if request.method == 'POST':
        form = MetricValueForm(request.POST, instance=metric_value, metric_type=metric_value.metric_type)
        if form.is_valid():
            metric_value = form.save(commit=False)
            metric_value.source = 'USER'  # Update source on edit
            
            # Ensure proper hierarchy is maintained
            if metric_value.metric_type.scope_type == 'PORTFOLIO':
                metric_value.portfolio = portfolio
                metric_value.position = None
                metric_value.transaction = None
            elif metric_value.metric_type.scope_type == 'POSITION':
                metric_value.position = position
                metric_value.portfolio = None
                metric_value.transaction = None
            elif metric_value.metric_type.scope_type == 'TRANSACTION':
                # Make sure the transaction is still set from when we loaded the object
                # Don't set or clear position/portfolio - should be None already from model validation
                pass
            
            metric_value.save()
            messages.success(request, f'{metric_value.metric_type.name} value updated successfully!')
            
            # Redirect based on scope type
            if metric_value.metric_type.scope_type == 'TRANSACTION':
                if position_id:  # Ensure position_id is not None
                    return redirect('metrics:transaction_metrics', 
                                  portfolio_id=portfolio_id, 
                                  position_id=position_id,
                                  transaction_id=metric_value.transaction.transaction_id)
                else:
                    return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
            elif metric_value.metric_type.scope_type == 'POSITION':
                if position_id:  # Ensure position_id is not None
                    return redirect('metrics:position_metrics', 
                                  portfolio_id=portfolio_id, 
                                  position_id=position_id)
                else:
                    return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
            else:  # PORTFOLIO scope
                return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
    else:
        form = MetricValueForm(instance=metric_value, metric_type=metric_value.metric_type)
    
    context = {
        'form': form,
        'portfolio': portfolio,
        'metric_type': metric_value.metric_type,
        'title': f'Edit {metric_value.metric_type.name} Value',
        'submit_text': 'Update'
    }
    
    if position:
        context['position'] = position
    
    if transaction or metric_value.transaction:
        context['transaction'] = transaction or metric_value.transaction
    
    return render(request, 'metrics/metric_value_form.html', context)

@login_required
def metric_update(request, portfolio_id, position_id, metric_type_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
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
            metric.source = 'USER'
            metric.save()
            messages.success(request, f'{metric_type.name} updated successfully.')
            return redirect('portfolio:position_detail', portfolio_id=portfolio_id, position_id=position_id)
    else:
        initial_data = {}
        if metric:
            initial_data = {'date': metric.date, 'value': metric.value}
        else:
            initial_data = {'date': datetime.date.today()}
        form = MetricUpdateForm(instance=metric, initial=initial_data)
    
    context = {
        'form': form,
        'portfolio': portfolio,
        'position': position,
        'metric_type': metric_type,
        'metric': metric,
    }
    return render(request, 'metrics/metric_update.html', context)

def get_metrics_by_type():
    """Helper function to get metrics grouped by type"""
    metric_types = MetricType.objects.all().order_by('scope_type', 'computation_order', 'name')
    
    # Group metrics by scope type
    metrics_by_type = {}
    for metric_type in metric_types:
        scope_display = dict(MetricType.SCOPE_TYPES)[metric_type.scope_type]
        if scope_display not in metrics_by_type:
            metrics_by_type[scope_display] = []
        metrics_by_type[scope_display].append(metric_type)
    
    return metrics_by_type

@login_required
def metric_types_list(request):
    """View to render the metrics list template"""
    metrics_by_type = get_metrics_by_type()
    return render(request, 'metrics/components/metric_types_list.html', {
        'metrics_by_type': metrics_by_type
    })

def get_position_metrics(position):
    """Get all metrics for a position"""
    # Get only position-scoped metrics
    metric_types = MetricType.objects.filter(scope_type='POSITION').order_by('computation_order', 'name')
    position_metrics = []
    
    for metric_type in metric_types:
        if metric_type.is_computed:
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
    
    return position_metrics

@login_required
def metric_history(request, portfolio_id, position_id=None, metric_id=None):
    """View metric history"""
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = None
    if position_id:
        position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    metric_type = get_object_or_404(MetricType, metric_id=metric_id)
    
    # Get all values for this metric based on its scope
    if metric_type.scope_type == 'TRANSACTION':
        if not position:
            messages.error(request, 'Cannot view transaction metrics without a position.')
            return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
        
        # For transaction metrics, we need the transaction_id from the query params
        transaction_id = request.GET.get('transaction_id')
        if not transaction_id:
            messages.error(request, 'No transaction specified.')
            return redirect('metrics:position_metrics', portfolio_id=portfolio_id, position_id=position_id)
        
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id, position=position)
        values = MetricValue.objects.filter(
            metric_type=metric_type,
            transaction=transaction
        ).order_by('-date')
        
        context = {
            'portfolio': portfolio,
            'position': position,
            'transaction': transaction,
            'metric_type': metric_type,
            'values': values
        }
        
    elif metric_type.scope_type == 'POSITION':
        if not position:
            messages.error(request, 'Cannot view position metrics without a position.')
            return redirect('metrics:portfolio_metrics', portfolio_id=portfolio_id)
        
        values = MetricValue.objects.filter(
            metric_type=metric_type,
            position=position
        ).order_by('-date')
        
        context = {
            'portfolio': portfolio,
            'position': position,
            'metric_type': metric_type,
            'values': values
        }
        
    else:  # PORTFOLIO scope
        values = MetricValue.objects.filter(
            metric_type=metric_type,
            portfolio=portfolio
        ).order_by('-date')
        
        context = {
            'portfolio': portfolio,
            'metric_type': metric_type,
            'values': values
        }
    
    return render(request, 'metrics/metric_history.html', context)

@login_required
def transaction_metrics(request, portfolio_id, position_id, transaction_id):
    """View for displaying transaction metrics"""
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, position=position)
    
    # Get transaction-scoped metrics ordered by computation_order
    all_metrics = MetricType.objects.filter(scope_type='TRANSACTION').order_by('computation_order', 'name')
    metrics_by_type = {}
    
    for metric in all_metrics:
        if metric.is_computed:
            # Compute the value
            value = metric.compute_value(transaction)
            if value is not None:
                computed_value = MetricValue(
                    transaction=transaction,
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
                transaction=transaction,
                metric_type=metric
            ).order_by('-date')
            
            # Always include the metric, even if it has no values
            if stored_values.exists():
                metrics_by_type[metric] = list(stored_values)
            else:
                # Create an empty metric value to show the metric in the list
                empty_value = MetricValue(
                    transaction=transaction,
                    metric_type=metric,
                    date=datetime.date.today(),
                    source='USER'
                )
                metrics_by_type[metric] = [empty_value]
    
    return render(request, 'metrics/transaction_metrics.html', {
        'portfolio': portfolio,
        'position': position,
        'transaction': transaction,
        'metrics_by_type': metrics_by_type
    })

@login_required
def portfolio_metrics(request, portfolio_id):
    """View for displaying portfolio metrics"""
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    
    # Get portfolio-scoped metrics ordered by computation_order
    all_metrics = MetricType.objects.filter(scope_type='PORTFOLIO').order_by('computation_order', 'name')
    metrics_by_type = {}
    
    for metric in all_metrics:
        if metric.is_computed:
            # Compute the value
            value = metric.compute_value(portfolio)
            if value is not None:
                computed_value = MetricValue(
                    portfolio=portfolio,
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
                portfolio=portfolio,
                metric_type=metric
            ).order_by('-date')
            
            # Always include the metric, even if it has no values
            if stored_values.exists():
                metrics_by_type[metric] = list(stored_values)
            else:
                # Create an empty metric value to show the metric in the list
                empty_value = MetricValue(
                    portfolio=portfolio,
                    metric_type=metric,
                    date=datetime.date.today(),
                    source='USER'
                )
                metrics_by_type[metric] = [empty_value]
    
    return render(request, 'metrics/portfolio_metrics.html', {
        'portfolio': portfolio,
        'metrics_by_type': metrics_by_type
    })

def get_portfolio_metrics(portfolio):
    """Get all metrics for a portfolio"""
    # Get only portfolio-scoped metrics
    metric_types = MetricType.objects.filter(scope_type='PORTFOLIO').order_by('computation_order', 'name')
    portfolio_metrics = []
    
    for metric_type in metric_types:
        if metric_type.is_computed:
            computed_value = metric_type.compute_value(portfolio)
            metric = MetricValue(
                portfolio=portfolio,
                metric_type=metric_type,
                date=datetime.date.today(),
                value=computed_value,
                source='COMPUTED'
            )
            portfolio_metrics.append(metric)
        else:
            latest_metric = MetricValue.objects.filter(
                portfolio=portfolio,
                metric_type=metric_type
            ).order_by('-date', '-created_at').first()
            
            if not latest_metric:
                latest_metric = MetricValue(
                    portfolio=portfolio,
                    metric_type=metric_type,
                    date=datetime.date.today(),
                    value=None,
                    source='USER'
                )
            portfolio_metrics.append(latest_metric)
    
    return portfolio_metrics

def get_specific_metric(position, metric_name):
    """
    Get a specific metric value for a position
    
    Args:
        position: Position object
        metric_name: Name of the metric to fetch
        
    Returns:
        MetricValue object or None if not found
    """
    from metrics.models import MetricType, MetricValue
    
    try:
        metric_type = MetricType.objects.get(name=metric_name)
        return MetricValue.objects.filter(
            position=position,
            metric_type=metric_type
        ).order_by('-date').first()
    except Exception:
        return None
