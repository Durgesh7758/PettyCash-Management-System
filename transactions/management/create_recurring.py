from django.core.management.base import BaseCommand
from transactions.models import RecurringTransaction, Transaction
from datetime import date, timedelta

class Command(BaseCommand):
    help = "Create recurring transactions if due"

    def handle(self, *args, **options):
        today = date.today()
        recurring = RecurringTransaction.objects.filter(active=True, next_due_date__lte=today)

        for r in recurring:
            t = r.transaction
            Transaction.objects.create(
                party=t.party,
                txn_type=t.txn_type,
                category=t.category,
                amount=t.amount,
                payment_mode=t.payment_mode,
                description=f"Recurring: {t.description}",
                date=t.next_due_date,
                created_by=t.created_by,
            )

            # Update next due date
            if r.frequency == 'daily':
                r.next_due_date += timedelta(days=1)
            elif r.frequency == 'weekly':
                r.next_due_date += timedelta(weeks=1)
            elif r.frequency == 'monthly':
                month = r.next_due_date.month + 1
                year = r.next_due_date.year
                if month > 12:
                    month = 1
                    year += 1
                r.next_due_date = r.next_due_date.replace(year=year, month=month)

            r.save()

        self.stdout.write(self.style.SUCCESS(f"Processed {recurring.count()} recurring transactions."))
