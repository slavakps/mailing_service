from django.db import models
from django.utils import timezone

from users.models import User


class Client(models.Model):
    email = models.EmailField(verbose_name="Email")
    FIO = models.CharField(max_length=100, verbose_name="ФИО")
    comment = models.TextField(verbose_name="Комментарий")
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Владелец", null=True, blank=True
    )

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.email


class Message(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    body = models.TextField(verbose_name="Текст письма")
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Владелец", null=True, blank=True
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.title


class Mailing(models.Model):
    STATUSES = (
        ("created", "создана"),
        ("started", "запущена"),
        ("finally", "завершена"),
    )
    start_datetime = models.DateTimeField(verbose_name="Время начала")
    end_datetime = models.DateTimeField(verbose_name="Время окончания")
    status = models.CharField(
        choices=STATUSES, verbose_name="Статус", default="created", max_length=50
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Сообщения"
    )
    recipients = models.ManyToManyField(Client, verbose_name="Получатели")
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Владелец", null=True, blank=True
    )

    def update_status(self):
        now = timezone.now()

        if now < self.start_datetime:
            new_status = "created"
        elif self.start_datetime <= now <= self.end_datetime:
            new_status = "started"
        else:
            new_status = "finished"

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка {self.start_datetime} {self.end_datetime}"


class Attempt(models.Model):
    attempt_datetime = models.DateTimeField(verbose_name="время отправки")
    STATUSES = (("ok", "успешно"), ("error", "не успешно"))
    status = models.CharField(
        choices=STATUSES, verbose_name="Статус", default="ok", max_length=50
    )
    server_response = models.CharField(
        max_length=255, verbose_name="ответ сервера", null=True, blank=True
    )
    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, verbose_name="Рассылка"
    )

    class Meta:
        verbose_name = "Попытка"
        verbose_name_plural = "Попытки"

    def __str__(self):
        return f"{self.attempt_datetime} {self.status}"
