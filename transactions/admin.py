from django.contrib import admin
from .models import Party, Transaction, Category, RecurringTransaction

# Party
@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name','phone','email','created_at')
    search_fields = ('name','phone','email')

# Transaction
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('txn_type','amount','payment_mode','party','category','date','created_by','created_at')
    list_filter = ('txn_type','payment_mode','date','category')
    search_fields = ('description','party__name','category__name')

# Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# RecurringTransaction
try:
    @admin.register(RecurringTransaction)
    class RecurringTransactionAdmin(admin.ModelAdmin):
        list_display = ('transaction', 'frequency', 'next_due_date', 'active')
        list_filter = ('frequency','active')
        search_fields = ('transaction__description','transaction__party__name')
except admin.sites.AlreadyRegistered:
    pass
