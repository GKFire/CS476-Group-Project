from django.core.management.base import BaseCommand

from sclibrary import notifications, services


class Command(BaseCommand):
    help = "Notify lenders and borrowers about active loans past their return date."

    def handle(self, *args, **options):
        count = 0
        for req in services.overdue_requests():
            notifications.notify_overdue(req)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Sent overdue notices for {count} loan(s)."))
