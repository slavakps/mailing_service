# Mailing Service

Учебный Django-проект сервиса рассылок.

## Функциональность
- CRUD клиентов
- CRUD сообщений
- CRUD рассылок
- Разграничение прав доступа
- Динамический статус рассылки

## Установка
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

## Запуск
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
