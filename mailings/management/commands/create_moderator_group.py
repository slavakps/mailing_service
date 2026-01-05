from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Создаёт группу Модератор с нужными правами"

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Модераторы")

        perms = Permission.objects.filter(
            codename__in=[
                # Клиенты
                "view_client",
                "change_client",

                # Рассылки
                "view_mailing",
                "change_mailing",

                # Пользователи
                "view_user",
                "change_user",
            ]
        )

        group.permissions.set(perms)

        self.stdout.write(
            self.style.SUCCESS(
                "Группа 'Модераторы' создана и права назначены"
                if created else
                "Группа 'Модераторы' уже существовала — права обновлены"
            )
        )
