import os

from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создаем экземпляр Celery
app = Celery("config")

# Загружаем конфигурацию из настроек Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение задач (tasks) из приложений Django
app.autodiscover_tasks()

# Настройка celery-beat
app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
