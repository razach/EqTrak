from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from portfolio.models import Portfolio, Position
from .models import MetricType, MetricValue
from .forms import MetricTypeForm, MetricValueForm, MetricUpdateForm
import datetime
from itertools import groupby
from operator import attrgetter

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
    
    return render(request, 'metrics/position_metrics.html', {
        'portfolio': portfolio,
        'position': position,
        'metrics_by_type': metrics_by_type
    })

@login_required
def metric_value_create(request, portfolio_id, position_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    
    # Get the metric type from query parameters
    metric_type_id = request.GET.get('metric_type')
    if not metric_type_id:
        messages.error(request, 'No metric type specified.')
        return redirect('metrics:position_metrics', portfolio_id=portfolio_id, position_id=position_id)
    
    metric_type = get_object_or_404(MetricType, metric_id=metric_type_id)
    
    if request.method == 'POST':
        form = MetricValueForm(request.POST, metric_type=metric_type)
        if form.is_valid():
            metric_value = form.save(commit=False)
            metric_value.position = position
            metric_value.metric_type = metric_type
            metric_value.source = 'USER'
            metric_value.save()
            messages.success(request, f'{metric_type.name} value added successfully!')
            return redirect('metrics:position_metrics', portfolio_id=portfolio_id, position_id=position_id)
    else:
        form = MetricValueForm(
            metric_type=metric_type,
            initial={'date': datetime.date.today()}
        )
    
    return render(request, 'metrics/metric_value_form.html', {
        'form': form,
        'portfolio': portfolio,
        'position': position,
        'metric_type': metric_type,
        'title': f'Add {metric_type.name} Value',
        'submit_text': 'Add'
    })

@login_required
def metric_value_edit(request, portfolio_id, position_id, value_id):
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    metric_value = get_object_or_404(MetricValue, value_id=value_id, position=position)
    
    if request.method == 'POST':
        form = MetricValueForm(request.POST, instance=metric_value, metric_type=metric_value.metric_type)
        if form.is_valid():
            metric_value = form.save(commit=False)
            metric_value.source = 'USER'  # Update source on edit
            metric_value.save()
            messages.success(request, f'{metric_value.metric_type.name} value updated successfully!')
            return redirect('metrics:position_metrics', portfolio_id=portfolio_id, position_id=position_id)
    else:
        form = MetricValueForm(instance=metric_value, metric_type=metric_value.metric_type)
    
    return render(request, 'metrics/metric_value_form.html', {
        'form': form,
        'portfolio': portfolio,
        'position': position,
        'metric_type': metric_value.metric_type,
        'title': f'Edit {metric_value.metric_type.name} Value',
        'submit_text': 'Update'
    })

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

@login_required
def metric_types_list(request):
    metric_types = MetricType.objects.all().order_by('category', 'name')
    
    # Group metrics by category
    metrics_by_category = {}
    for category, metrics in groupby(metric_types, key=attrgetter('category')):
        metrics_by_category[dict(MetricType.CATEGORIES)[category]] = list(metrics)
    
    return {
        'metrics_by_category': metrics_by_category
    }

def get_position_metrics(position):
    """Get all metrics for a position"""
    metric_types = MetricType.objects.all()
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
