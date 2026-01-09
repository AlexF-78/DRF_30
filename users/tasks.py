import time
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@shared_task
def deactivate_inactive_users():
    """
    Проверяет пользователей по дате последнего входа (last_login).
    Если пользователь не заходил более месяца - блокирует его (is_active=False).
    """
    # Дата "месяц назад" от текущего времени
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим и деактивируем неактивных пользователей
    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_active=True)

    count = inactive_users.count()
    inactive_users.update(is_active=False)

    return f"Деактивировано {count} пользователей"


@shared_task
def test_task():
    """Тестовая задача"""
    print("Тестовая задача Celery выполнена!")
    time.sleep(5)  # Имитация долгой задачи
    return "Задача успешно выполнена"
