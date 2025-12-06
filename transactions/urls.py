from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Parties
    path('parties/', views.party_list, name='party_list'),
    path('parties/add/', views.party_add, name='party_add'),
    path('parties/<int:pk>/edit/', views.party_edit, name='party_edit'),
    path('parties/<int:pk>/delete/', views.party_delete, name='party_delete'),

    # Transactions
    path('', views.transaction_list, name='transaction_list'),
    path('add/', views.transaction_add, name='transaction_add'),
    path('<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),

    # Exports
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),

    # Payment-mode specific pages
    path('upi/', views.upi_view, name='upi'),
    path('cash/', views.cash_view, name='cash'),
    path('card/', views.card_view, name='card'),
    path('bank-transfer/', views.bank_transfer_view, name='bank_transfer'),
]
