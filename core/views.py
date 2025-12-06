# core/views.py
from django.shortcuts import render
from transactions.models import Transaction
from django.db.models import Sum
from datetime import date, timedelta

def dashboard(request):
    # basic summary
    today = date.today()
    total_income = Transaction.objects.filter(txn_type='IN').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Transaction.objects.filter(txn_type='OUT').aggregate(total=Sum('amount'))['total'] or 0
    balance = total_income - total_expense

    recent_txns = Transaction.objects.all()[:8]
    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'recent_txns': recent_txns,
    }
    return render(request, 'core/dashboard.html', context)


def home(request):
    return render(request, 'core/home.html')
