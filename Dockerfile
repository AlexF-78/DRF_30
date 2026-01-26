# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем системные зависимости, необходимые для Postgres и других пакетов
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock /app/

# Настраиваем Poetry не создавать виртуальное окружение внутри контейнера
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости (только основные, без dev)
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Копируем весь проект
COPY . /app/

# Создаем директории для статики и медиа
RUN mkdir -p /app/staticfiles /app/media

# Открываем порт 8000 для взаимодействия с приложением
EXPOSE 8000

# Определяем команду для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
