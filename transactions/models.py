from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

User = get_user_model()

PAYMENT_CHOICES = [
    ('Cash','Cash'),
    ('UPI','UPI'),
    ('Bank','Bank'),
    ('Card','Card'),
    ('Wallet','Wallet'),
    ('Other','Other'),
]

TXN_TYPE = [
    ('IN','Income'),
    ('OUT','Expense'),
]

class Party(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, blank=True)
    txn_type = models.CharField(max_length=3, choices=TXN_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Cash')

    # extra payment fields
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    upi_ref = models.CharField(max_length=150, blank=True, null=True)
    bank_name = models.CharField(max_length=150, blank=True, null=True)
    bank_account = models.CharField(max_length=50, blank=True, null=True)
    bank_ref = models.CharField(max_length=150, blank=True, null=True)
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    wallet_provider = models.CharField(max_length=50, blank=True, null=True)
    other_note = models.CharField(max_length=255, blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Add category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        ordering = ['-date','-created_at']

    def __str__(self):
        return f"{self.get_txn_type_display()} - {self.amount}"


FREQUENCY_CHOICES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
]

class RecurringTransaction(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    next_due_date = models.DateField()
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction} ({self.frequency})"


FREQUENCY_CHOICES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
]

class RecurringTransaction(models.Model):
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    next_due_date = models.DateField(default=timezone.now)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction} | {self.frequency} | Next: {self.next_due_date}"



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"
