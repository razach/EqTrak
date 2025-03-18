from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from datetime import date

from .models import UserDefinedMetric
from .forms import UserDefinedMetricForm, UserMetricValueForm
from metrics.models import MetricType, MetricValue
from portfolio.models import Portfolio, Position, Transaction

@login_required
def user_metric_list(request):
    """Display all user-defined metrics for the current user"""
    # Ensure we only show metrics for the current user
    metrics = UserDefinedMetric.objects.filter(user=request.user)
    
    context = {
        'metrics': metrics,
        'title': 'My Custom Metrics',
    }
    return render(request, 'user_metrics/metric_list.html', context)

@login_required
def create_user_metric(request):
    """Create a new user-defined metric"""
    if request.method == 'POST':
        form = UserDefinedMetricForm(request.POST, user=request.user)
        if form.is_valid():
            user_metric = form.save()
            messages.success(request, f'Custom metric "{user_metric.name}" created successfully!')
            return redirect('user_metrics:list')
    else:
        form = UserDefinedMetricForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create Custom Metric',
        'data_type_choices': MetricType.DATA_TYPES,
        'scope_type_choices': MetricType.SCOPE_TYPES
    }
    return render(request, 'user_metrics/metric_form.html', context)

@login_required
def edit_user_metric(request, pk):
    """Edit an existing user-defined metric"""
    # Ensure we only allow editing user's own metrics
    user_metric = get_object_or_404(UserDefinedMetric, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = UserDefinedMetricForm(request.POST, instance=user_metric, user=request.user)
        if form.is_valid():
            user_metric = form.save()
            messages.success(request, f'Custom metric "{user_metric.name}" updated successfully!')
            return redirect('user_metrics:list')
    else:
        form = UserDefinedMetricForm(instance=user_metric, user=request.user)
    
    context = {
        'form': form,
        'metric': user_metric,
        'title': f'Edit Custom Metric: {user_metric.name}',
        'data_type_choices': MetricType.DATA_TYPES,
        'scope_type_choices': MetricType.SCOPE_TYPES
    }
    return render(request, 'user_metrics/metric_form.html', context)

@login_required
def delete_user_metric(request, pk):
    """Delete a user-defined metric"""
    # Ensure we only allow deleting user's own metrics
    user_metric = get_object_or_404(UserDefinedMetric, pk=pk, user=request.user)
    
    if request.method == 'POST':
        metric_name = user_metric.name
        
        # Delete the associated metric values
        metric_type = user_metric.metric_type
        MetricValue.objects.filter(metric_type=metric_type).delete()
        
        # Delete the user metric and its metric type
        metric_type_pk = metric_type.pk
        user_metric.delete()
        
        # Clean up orphaned metric type
        try:
            orphaned_metric_type = MetricType.objects.get(pk=metric_type_pk)
            orphaned_metric_type.delete()
        except MetricType.DoesNotExist:
            pass
        
        messages.success(request, f'Custom metric "{metric_name}" deleted successfully!')
        return redirect('user_metrics:list')
    
    context = {
        'metric': user_metric,
        'title': f'Delete Custom Metric: {user_metric.name}',
    }
    return render(request, 'user_metrics/metric_confirm_delete.html', context)

@login_required
def add_metric_value(request, metric_id, portfolio_id=None, position_id=None, transaction_id=None):
    """Add a value to a user-defined metric"""
    # Ensure we only allow adding values to user's own metrics
    user_metric = get_object_or_404(UserDefinedMetric, pk=metric_id, user=request.user)
    metric_type = user_metric.metric_type
    
    # Get the target objects
    portfolio = None
    position = None
    transaction = None
    
    if portfolio_id:
        portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    
    if position_id and portfolio:
        position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    
    if transaction_id and position:
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id, position=position)
    
    # Determine the appropriate target based on metric scope
    if metric_type.scope_type == 'PORTFOLIO' and not portfolio:
        messages.error(request, "Portfolio is required for this metric.")
        return redirect('user_metrics:list')
    elif metric_type.scope_type == 'POSITION' and not position:
        messages.error(request, "Position is required for this metric.")
        return redirect('user_metrics:list')
    elif metric_type.scope_type == 'TRANSACTION' and not transaction:
        messages.error(request, "Transaction is required for this metric.")
        return redirect('user_metrics:list')
    
    if request.method == 'POST':
        form = UserMetricValueForm(request.POST, metric_type=metric_type, user_metric=user_metric)
        if form.is_valid():
            metric_value = form.save(commit=False)
            metric_value.metric_type = metric_type
            
            # Set the appropriate target
            if metric_type.scope_type == 'PORTFOLIO':
                metric_value.portfolio = portfolio
            elif metric_type.scope_type == 'POSITION':
                metric_value.position = position
            elif metric_type.scope_type == 'TRANSACTION':
                metric_value.transaction = transaction
            
            metric_value.source = 'USER'
            metric_value.save()
            
            # Update the latest_value reference
            user_metric.latest_value = metric_value
            user_metric.save()
            
            messages.success(request, f'Value added to "{user_metric.name}" successfully!')
            
            # Determine redirect target
            if transaction:
                return redirect('metrics:transaction_metrics', portfolio_id=portfolio.portfolio_id, 
                              position_id=position.position_id, transaction_id=transaction.transaction_id)
            elif position:
                return redirect('metrics:position_metrics', portfolio_id=portfolio.portfolio_id, 
                              position_id=position.position_id)
            else:
                return redirect('metrics:portfolio_metrics', portfolio_id=portfolio.portfolio_id)
    else:
        form = UserMetricValueForm(
            metric_type=metric_type,
            user_metric=user_metric,
            initial={'date': date.today()}
        )
    
    # Determine back URL
    back_url = None
    if transaction:
        back_url = reverse('metrics:transaction_metrics', kwargs={
            'portfolio_id': portfolio.portfolio_id, 
            'position_id': position.position_id,
            'transaction_id': transaction.transaction_id
        })
    elif position:
        back_url = reverse('metrics:position_metrics', kwargs={
            'portfolio_id': portfolio.portfolio_id, 
            'position_id': position.position_id
        })
    elif portfolio:
        back_url = reverse('metrics:portfolio_metrics', kwargs={
            'portfolio_id': portfolio.portfolio_id
        })
    
    context = {
        'form': form,
        'user_metric': user_metric,
        'metric_type': metric_type,
        'portfolio': portfolio,
        'position': position,
        'transaction': transaction,
        'title': f'Add Value for {user_metric.name}',
        'back_url': back_url
    }
    
    return render(request, 'user_metrics/metric_value_form.html', context) 