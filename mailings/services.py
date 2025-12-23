from django.core.mail import send_mail
from django.utils import timezone

from .models import Attempt, Mailing


def send_mailing(mailing: Mailing):
    mailing.update_status()

    if mailing.status != "started":
        return f"Рассылка не может быть отправлена. Текущий статус: {mailing.status}"

    for client in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.title,
                message=mailing.message.body,
                from_email="slavakpss99@bk.ru",
                recipient_list=[client.email],
            )
            Attempt.objects.create(
                mailing=mailing,
                status="ok",
                attempt_datetime=timezone.now(),
                server_response="Email отправлен успешно",
            )
        except Exception as e:
            Attempt.objects.create(
                mailing=mailing,
                status="error",
                attempt_datetime=timezone.now(),
                server_response=str(e),
            )
