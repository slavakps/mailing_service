from django.core.management.base import BaseCommand
from django.utils import timezone

from mailings.models import Mailing
from mailings.services import send_mailing


class Command(BaseCommand):
    help = "Отправляет активные рассылки"

    def handle(self, *args, **options):
        now = timezone.now()

        mailings = Mailing.objects.filter(
            start_datetime__lte=now,
            end_datetime__gte=now,
        )

        if not mailings.exists():
            self.stdout.write(self.style.WARNING("Нет рассылок для отправки"))
            return

        for mailing in mailings:
            self.stdout.write(f"Отправка рассылки #{mailing.id}")
            send_mailing(mailing)

        self.stdout.write(self.style.SUCCESS("Готово"))
