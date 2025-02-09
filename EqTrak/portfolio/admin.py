from django.contrib import admin
from .models import Portfolio, Position, Transaction

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'currency', 'is_active', 'created_at')
    list_filter = ('is_active', 'currency')
    search_fields = ('name', 'user__username')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'portfolio', 'position_type', 'is_active')
    list_filter = ('position_type', 'is_active', 'portfolio')
    search_fields = ('ticker', 'portfolio__name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'position', 'quantity', 'price', 'date', 'status')
    list_filter = ('transaction_type', 'status', 'date')
    search_fields = ('position__ticker', 'notes') 