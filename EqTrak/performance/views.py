from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from portfolio.models import Portfolio, Position, Transaction
from .models import PerformanceMetric, PerformanceSettings
from .services import PerformanceService

@login_required
def performance_dashboard(request):
    """
    Main performance dashboard showing performance across user's portfolios.
    """
    # Check if performance feature is enabled
    if not PerformanceService.is_performance_enabled(user=request.user):
        messages.warning(request, "Performance tracking is currently disabled. Please enable it in your settings.")
        return redirect('portfolio:home')
    
    # Get user's portfolios
    portfolios = Portfolio.objects.filter(user=request.user)
    
    # Calculate performance for each portfolio
    for portfolio in portfolios:
        PerformanceService.calculate_portfolio_performance(portfolio, user=request.user)
    
    context = {
        'portfolios': portfolios,
        'title': 'Performance Dashboard'
    }
    
    return render(request, 'performance/dashboard.html', context)

@login_required
def portfolio_performance(request, portfolio_id):
    """
    Detailed performance view for a specific portfolio.
    """
    # Check if performance feature is enabled
    if not PerformanceService.is_performance_enabled(user=request.user):
        messages.warning(request, "Performance tracking is currently disabled. Please enable it in your settings.")
        return redirect('portfolio:detail', portfolio_id=portfolio_id)
    
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    
    # Calculate latest performance metrics
    performance = PerformanceService.calculate_portfolio_performance(portfolio, user=request.user)
    
    # Get all positions in this portfolio
    positions = portfolio.position_set.all()
    
    # Calculate performance for each position
    for position in positions:
        PerformanceService.calculate_position_performance(position, user=request.user)
    
    context = {
        'portfolio': portfolio,
        'performance': performance,
        'positions': positions,
        'title': f'{portfolio.name} Performance'
    }
    
    return render(request, 'performance/portfolio_performance.html', context)

@login_required
def position_performance(request, portfolio_id, position_id):
    """
    Detailed performance view for a specific position.
    """
    # Check if performance feature is enabled
    if not PerformanceService.is_performance_enabled(user=request.user):
        messages.warning(request, "Performance tracking is currently disabled. Please enable it in your settings.")
        return redirect('portfolio:position_detail', portfolio_id=portfolio_id, position_id=position_id)
    
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    
    # Calculate latest performance metrics
    performance = PerformanceService.calculate_position_performance(position, user=request.user)
    
    # Get transactions for this position
    transactions = position.transaction_set.filter(transaction_type='SELL')
    
    # Calculate performance for each transaction
    for transaction in transactions:
        PerformanceService.calculate_transaction_performance(transaction, user=request.user)
    
    context = {
        'portfolio': portfolio,
        'position': position,
        'performance': performance,
        'transactions': transactions,
        'title': f'{position.security_name} Performance'
    }
    
    return render(request, 'performance/position_performance.html', context)

@login_required
def transaction_performance(request, portfolio_id, position_id, transaction_id):
    """
    Detailed performance view for a specific transaction.
    """
    # Check if performance feature is enabled
    if not PerformanceService.is_performance_enabled(user=request.user):
        messages.warning(request, "Performance tracking is currently disabled. Please enable it in your settings.")
        return redirect('portfolio:transaction_detail', portfolio_id=portfolio_id, position_id=position_id, transaction_id=transaction_id)
    
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, position=position)
    
    # Only SELL transactions have performance metrics
    if transaction.transaction_type != 'SELL':
        messages.info(request, "Performance metrics are only available for sell transactions.")
        return redirect('portfolio:transaction_detail', portfolio_id=portfolio_id, position_id=position_id, transaction_id=transaction_id)
    
    # Calculate latest performance metrics
    performance = PerformanceService.calculate_transaction_performance(transaction, user=request.user)
    
    context = {
        'portfolio': portfolio,
        'position': position,
        'transaction': transaction,
        'performance': performance,
        'title': f'Transaction Performance'
    }
    
    return render(request, 'performance/transaction_performance.html', context)

@login_required
def recalculate_all(request):
    """
    Recalculate all performance metrics for the user's data.
    """
    # Check if performance feature is enabled
    if not PerformanceService.is_performance_enabled(user=request.user):
        messages.warning(request, "Performance tracking is currently disabled. Please enable it in your settings.")
        return redirect('portfolio:home')
    
    # Perform calculations
    result = PerformanceService.calculate_all_performance(user=request.user)
    
    messages.success(
        request, 
        f"Performance metrics recalculated for {result['portfolios']} portfolios, "
        f"{result['positions']} positions, and {result['transactions']} transactions."
    )
    
    # Redirect back to referring page or dashboard
    return redirect(request.META.get('HTTP_REFERER', 'performance:dashboard'))

@login_required
def api_position_performance(request, position_id):
    """
    API endpoint to get performance data for a position.
    Used for AJAX requests.
    """
    # Check if performance feature is enabled
    if not PerformanceService.is_performance_enabled(user=request.user):
        return JsonResponse({'error': 'Performance tracking is disabled'}, status=403)
    
    try:
        position = get_object_or_404(Position, position_id=position_id)
        
        # Ensure the user has access to this position
        if position.portfolio.user != request.user:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Calculate performance
        performance = PerformanceService.calculate_position_performance(position, user=request.user)
        
        if not performance:
            return JsonResponse({'error': 'Failed to calculate performance'}, status=500)
        
        # Return performance data
        return JsonResponse({
            'cost_basis': float(performance.cost_basis),
            'current_value': float(performance.current_value),
            'absolute_gain_loss': float(performance.absolute_gain_loss),
            'percentage_gain_loss': float(performance.percentage_gain_loss),
            'is_realized': performance.is_realized,
            'calculation_date': performance.calculation_date.isoformat()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
