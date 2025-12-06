from django import forms
from .models import Party, Transaction
import datetime
from .models import Party, Transaction, Category  # <- Category import kar lo
from .models import RecurringTransaction


class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ['name', 'phone', 'email', 'address']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter party/vendor name',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email (optional)',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Address',
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return phone

        phone_str = str(phone).strip()

        if not phone_str.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")

        if len(phone_str) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits.")

        return phone_str


# -------------------------------
# TRANSACTION FORM
# -------------------------------

class TransactionForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=datetime.date.today
    )

    class Meta:
        model = Transaction
        fields = [
            'party',
            'txn_type',
            'category',  # <- add this
            'amount',
            'payment_mode',
            'description',
            'attachment',
            'date'
        ]

        widgets = {
            'party': forms.Select(attrs={'class': 'form-select'}),
            'txn_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),  # <- widget for category
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount',
                'min': '0.01',
                'step': '0.01'
            }),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description (optional)',
            }),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class RecurringTransactionForm(forms.ModelForm):
    class Meta:
        model = RecurringTransaction
        fields = ['transaction', 'frequency', 'next_due_date', 'active']
        widgets = {
            'transaction': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'next_due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        
    # clean_amount, clean_date, clean methods remain same


    def clean_amount(self):
        amt = self.cleaned_data.get('amount')
        if amt is None:
            raise forms.ValidationError("Amount is required.")
        if amt <= 0:
            raise forms.ValidationError("Enter a positive amount.")
        return amt

    def clean_date(self):
        d = self.cleaned_data.get('date')
        if not d:
            raise forms.ValidationError("Date is required.")
        if d > datetime.date.today():
            raise forms.ValidationError("Date cannot be in the future.")
        return d

    def clean(self):
        cleaned = super().clean()

        pm = cleaned.get('payment_mode')
        description = cleaned.get('description')

        # Example validation: If payment mode is 'Other', force description
        if pm == 'Other' and not description:
            self.add_error('description', "Please provide details for 'Other' payment mode.")

        return cleaned
