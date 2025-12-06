from django.shortcuts import render, get_object_or_404, redirect
from .models import Party, Transaction
from .forms import PartyForm, TransactionForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
import datetime
import io
import xlsxwriter
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas

# Parties
@login_required
def party_list(request):
    parties = Party.objects.all().order_by('name')
    return render(request, 'transactions/party_list.html', {'parties': parties})

@login_required
def party_add(request):
    if request.method == 'POST':
        form = PartyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Party added.")
            return redirect('transactions:party_list')
    else:
        form = PartyForm()
    return render(request, 'transactions/party_form.html', {'form': form})

@login_required
def party_edit(request, pk):
    party = get_object_or_404(Party, pk=pk)
    if request.method == 'POST':
        form = PartyForm(request.POST, instance=party)
        if form.is_valid():
            form.save()
            messages.success(request, "Party updated.")
            return redirect('transactions:party_list')
    else:
        form = PartyForm(instance=party)
    return render(request, 'transactions/party_form.html', {'form': form, 'edit': True})

@login_required
def party_delete(request, pk):
    party = get_object_or_404(Party, pk=pk)
    if request.method == 'POST':
        party.delete()
        messages.success(request, "Party deleted.")
        return redirect('transactions:party_list')
    return render(request, 'transactions/party_confirm_delete.html', {'party': party})


# Transactions
@login_required
def transaction_list(request):
    qs = Transaction.objects.select_related('party','created_by').all()
    # filters: date range, type, party
    start = request.GET.get('start')
    end = request.GET.get('end')
    ttype = request.GET.get('type')
    party_id = request.GET.get('party')
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    if ttype in ('IN','OUT'):
        qs = qs.filter(txn_type=ttype)
    if party_id:
        qs = qs.filter(party_id=party_id)

    total_in = qs.filter(txn_type='IN').aggregate(total=Sum('amount'))['total'] or 0
    total_out = qs.filter(txn_type='OUT').aggregate(total=Sum('amount'))['total'] or 0

    parties = Party.objects.all()
    context = {
        'transactions': qs,
        'total_in': total_in,
        'total_out': total_out,
        'parties': parties,
    }
    return render(request, 'transactions/transaction_list.html', context)

@login_required
def transaction_add(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            txn = form.save(commit=False)
            txn.created_by = request.user
            txn.save()
            messages.success(request, "Transaction saved.")
            return redirect('transactions:transaction_list')
    else:
        form = TransactionForm(initial={'date': datetime.date.today()})
    return render(request, 'transactions/transaction_form.html', {'form': form})

@login_required
def transaction_edit(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, instance=txn)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated.")
            return redirect('transactions:transaction_list')
    else:
        form = TransactionForm(instance=txn)
    return render(request, 'transactions/transaction_form.html', {'form': form, 'edit': True})

@login_required
def transaction_delete(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        txn.delete()
        messages.success(request, "Transaction deleted.")
        return redirect('transactions:transaction_list')
    return render(request, 'transactions/transaction_confirm_delete.html', {'txn': txn})


# Export to Excel
@login_required
def export_excel(request):
    qs = Transaction.objects.all().order_by('date')
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Transactions')
    headers = ['Date', 'Type','Party','Amount','Payment Mode','Description','Created By']
    for col, h in enumerate(headers):
        worksheet.write(0, col, h)
    for row, txn in enumerate(qs, start=1):
        worksheet.write(row, 0, str(txn.date))
        worksheet.write(row, 1, txn.get_txn_type_display())
        worksheet.write(row, 2, txn.party.name if txn.party else '')
        worksheet.write(row, 3, float(txn.amount))
        worksheet.write(row, 4, txn.payment_mode)
        worksheet.write(row, 5, txn.description or '')
        worksheet.write(row, 6, txn.created_by.username if txn.created_by else '')
    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=transactions.xlsx'
    return response

@login_required
def upi_view(request):
    # Add context if needed
    context = {}
    return render(request, 'transactions/upi.html', context)

@login_required
def cash_view(request):
    context = {}
    return render(request, 'transactions/cash.html', context)

@login_required
def card_view(request):
    context = {}
    return render(request, 'transactions/card.html', context)

@login_required
def bank_transfer_view(request):
    context = {}
    return render(request, 'transactions/bank_transfer.html', context)

@login_required
def upi_view(request):
    upi_txns = Transaction.objects.filter(payment_mode='UPI')
    return render(request, 'transactions/upi.html', {'transactions': upi_txns})

@login_required
def cash_view(request):
    cash_txns = Transaction.objects.filter(payment_mode='Cash')
    return render(request, 'transactions/cash.html', {'transactions': cash_txns})

@login_required
def card_view(request):
    card_txns = Transaction.objects.filter(payment_mode='Card')
    return render(request, 'transactions/card.html', {'transactions': card_txns})

@login_required
def bank_transfer_view(request):
    bank_txns = Transaction.objects.filter(payment_mode='Bank Transfer')
    return render(request, 'transactions/bank_transfer.html', {'transactions': bank_txns})



# Export to PDF (simple)
@login_required
def export_pdf(request):
    # Fetch transactions
    transactions = Transaction.objects.all().order_by('date')

    # Create a file-like buffer
    buffer = io.BytesIO()
    
    # PDF setup (landscape letter size)
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1  # center
    normal_style = styles['Normal']

    # Title
    elements.append(Paragraph("Petty Cash Transactions Report", title_style))
    elements.append(Spacer(1, 12))

    # Table data
    data = [["Date", "Type", "Party", "Amount", "Payment Mode", "Remarks"]]
    for txn in transactions:
        data.append([
            txn.date.strftime('%d-%m-%Y'),
            txn.get_txn_type_display(),
            txn.party.name if txn.party else '-',
            f"{txn.amount:.2f}",
            txn.payment_mode,
            txn.remarks if hasattr(txn, 'remarks') else ''
        ])

    # Table style
    table = Table(data, repeatRows=1, hAlign='LEFT', colWidths=[80,80,120,80,100,150])
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0d6efd")),  # Header background
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),                  # Header text color
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ])
    table.setStyle(style)

    # Alternate row colors
    for i in range(1, len(data)):
        bg_color = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
        table.setStyle(TableStyle([('BACKGROUND', (0,i), (-1,i), bg_color)]))

    elements.append(table)

    # Footer with page number
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(landscape(letter)[0] - 30, 20, text)

    # Build PDF
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
