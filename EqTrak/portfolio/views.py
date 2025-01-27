from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Portfolio, Position, Transaction
from .forms import PortfolioForm, PositionForm, TransactionForm
import datetime

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
            # Create position
            position = form.save(commit=False)
            position.portfolio = portfolio
            position.save()
            
            # Create initial BUY transaction
            transaction = Transaction.objects.create(
                position=position,
                transaction_type='BUY',
                quantity=position.shares,
                price=position.purchase_price,
                fees=0,
                date=datetime.date.today(),
                status='COMPLETED',
                currency=portfolio.currency
            )
            
            # Set initial cost basis
            position.cost_basis = position.shares * position.purchase_price
            position.save()
            
            messages.success(request, 'Position created successfully!')
            return redirect('portfolio:portfolio_detail', portfolio_id=portfolio_id)
    else:
        form = PositionForm()
    
    return render(request, 'portfolio/position_form.html', {
        'form': form,
        'portfolio': portfolio,
        'title': 'Add Position',
        'submit_text': 'Add'
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
    portfolio = get_object_or_404(Portfolio, portfolio_id=portfolio_id, user=request.user)
    position = get_object_or_404(Position, position_id=position_id, portfolio=portfolio)
    transactions = position.transaction_set.all().order_by('-date', '-created_at')
    
    return render(request, 'portfolio/position_detail.html', {
        'portfolio': portfolio,
        'position': position,
        'transactions': transactions
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
            
            # Recalculate position totals
            update_position_from_transactions(position)
            
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

def update_position_from_transactions(position):
    """Recalculate position totals based on all transactions."""
    transactions = position.transaction_set.filter(status='COMPLETED')
    
    total_shares = sum(t.shares_impact for t in transactions)
    total_cost = sum(t.transaction_impact for t in transactions)
    
    position.shares = total_shares
    if total_shares > 0:
        position.cost_basis = total_cost
        position.purchase_price = total_cost / total_shares
    else:
        position.cost_basis = 0
        position.purchase_price = 0
    
    position.save()
