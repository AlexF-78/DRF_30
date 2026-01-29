# Django REST API для курса обучения

## Описание проекта
Данный проект — образовательная платформа, реализованная на базе Django и Django REST Framework (DRF). 
В нем реализованы модели пользователей, курсов, уроков,
а также система платежей и разграничение доступа на основе ролей (пользователь, модератор).
Проект включает CRUD-операции, фильтрацию данных, авторизацию с помощью JWT и контроль доступа.

## Структура проекта
- `users` — приложение для управления пользователями и платежами
- `lms` (или `materials`) — приложение для управления курсами и уроками

В проекте используются сериализаторы, ViewSet и Generics для CRUD-операций.

## Основные возможности

### Модели:
- **Пользователь** (замена стандартной аутентификации на email, телефон, город, аватарка)
- **Курс** (название, превью, описание)
- **Урок** (название, описание, превью, ссылка на видео)
- **Связь между курсами и уроками** — один курс содержит много уроков

### В приложении `users` реализована модель **Платежи**:
- Пользователь
- Дата оплаты
- Оплаченный курс или урок (ссылки на модели)
- Сумма оплаты
- Способ оплаты (наличные, перевод)

### Реализованные функции:
- Простейшие сериализаторы и CRUD-операции с помощью Viewsets и Generics
- Работа API проверена через Postman
- В сериализатор модели курса добавлено поле количества уроков (SerializerMethodField)
- Модель Платежи с фикстурами для заполнения данных
- В сериализаторе курса добавлено поле со списком уроков и количеством уроков курса

### Фильтрация и сортировка:
- Порядок сортировки по дате оплаты
- Фильтр по курсу, уроку
- Фильтр по способу оплаты

### Авторизация и разграничение доступа:
- JWT-аутентификация
- Группы: пользователь, модератор
- Для модераторов задан ограниченный доступ (может редактировать, просматривать, но не создавать и не удалять курсы/уроки)
- Пользователи могут редактировать только свои курсы и уроки
- В `permissions.py` реализованы кастомные права: `IsModerator`, `IsOwner`
- Контроллеры настроены на разное право доступа посредством метода `get_permissions()`

---

##  Запуск с помощью Docker Compose

### Development окружение

#### Предварительные требования
- Установленный Docker и Docker Compose
- Файл `.env` с переменными окружения (на основе `.env.sample`)

#### Запуск проекта
```bash
# Собрать и запустить все сервисы
docker-compose up -d

# Остановить все сервисы
docker-compose down

# Просмотр логов
docker-compose logs -f web
Проверка работоспособности
Django приложение: http://localhost:8000

PostgreSQL: docker-compose exec db psql -U postgres -d drf_30_db

Redis: docker-compose exec redis redis-cli ping

Celery worker: docker-compose logs celery

Celery beat: docker-compose logs celery_beat

Полезные команды
bash
# Создать суперпользователя Django
docker-compose exec web python manage.py createsuperuser

# Выполнить миграции (выполняются автоматически при запуске)
docker-compose exec web python manage.py migrate

# Проверить статус сервисов
docker-compose ps

# Пересобрать образы
docker-compose build --no-cache

# Выполнить тесты
docker-compose exec web python manage.py test
Структура сервисов (Development)
web: Django приложение на порту 8000

db: PostgreSQL на порту 5433 (внешнем), 5432 (внутреннем)

redis: Redis на порту 6379

celery: Celery worker

celery_beat: Celery beat scheduler

 Production Deployment с Docker Compose
Настройка сервера (Ubuntu 24.04)
Установка Docker и Docker Compose:

bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
# Переподключитесь к серверу
Клонирование проекта:

bash
cd ~
mkdir -p projects
cd projects
git clone https://github.com/AlexF-78/DRF_30.git
cd DRF_30
Настройка production окружения:

bash
cp .env.prod.sample .env.prod
# Отредактируйте .env.prod с реальными production значениями:
# - DEBUG=False
# - SECRET_KEY=ваш_ключ
# - DB_HOST=db
# - REDIS_HOST=redis
# - ALLOWED_HOSTS=ваш_ip
# - Реальные пароли для БД и другие секреты
Запуск production сервисов:

bash
docker-compose -f docker-compose.prod.yml up -d
Проверка работоспособности:

bash
# Проверить запущенные контейнеры
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f nginx

# Проверить доступность
curl -I http://ваш_сервер_ip/
Структура production сервисов:
PostgreSQL: db:5432 (внутренняя сеть Docker)

Redis: redis:6379 (внутренняя сеть Docker)

Django + Gunicorn: web:8000 (внутренняя сеть Docker)

Nginx: 80:80 (публичный доступ)

Celery Worker: обработка фоновых задач

Celery Beat: планировщик задач

Полезные команды для production
bash
# Перезапустить все сервисы
docker-compose -f docker-compose.prod.yml restart

# Обновить контейнеры после изменений кода
docker-compose -f docker-compose.prod.yml up -d --build

# Остановить все сервисы
docker-compose -f docker-compose.prod.yml down

# Просмотр логов конкретного сервиса
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f nginx

# Выполнить команду в контейнере
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
 CI/CD с GitHub Actions и Docker
Проект настроен с автоматическим CI/CD пайплайном через GitHub Actions с использованием Docker.

Workflow файл: .github/workflows/django.yml

При каждом push в ветки develop или feature/homework_34_2:

Запускаются автоматические тесты с Python 3.12, PostgreSQL и Redis

Собираются Docker-образы для всех сервисов

Запускается покрытие кода (coverage)

Происходит автоматический деплой на продакшен сервер через Docker Compose

Особенности Docker-деплоя:

Systemd-сервисы (nginx, gunicorn) автоматически останавливаются

Все сервисы запускаются в изолированных Docker-контейнерах

Используется отдельный production Docker Compose файл (docker-compose.prod.yml)

Автоматическая очистка неиспользуемых образов

Настроенные Secrets в GitHub:

SERVER_HOST - IP адрес сервера

SERVER_USER - имя пользователя на сервере

SSH_PRIVATE_KEY - приватный SSH ключ

SECRET_KEY - секретный ключ Django

DATABASE_URL - строка подключения к БД

STRIPE_API_KEY, STRIPE_PUBLIC_KEY - ключи Stripe

Статус CI/CD:
https://github.com/AlexF-78/DRF_30/actions/workflows/django.yml/badge.svg

 Проверка работоспособности после Docker-деплоя
После деплоя проверьте:

Docker контейнеры:

bash
docker-compose -f docker-compose.prod.yml ps
Все сервисы должны быть в состоянии "Up"

Основной endpoint: http://ваш_сервер_ip/

Админ панель: http://ваш_сервер_ip/admin/

Логи:

bash
docker-compose -f docker-compose.prod.yml logs nginx
docker-compose -f docker-compose.prod.yml logs web
Systemd-сервисы должны быть остановлены:

bash
sudo systemctl status nginx gunicorn
# Должно быть "inactive (dead)"
Проверка подключения к БД:

bash
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d drf_30_prod -c "\l"
 Ручная настройка (без Docker)
Установка зависимостей
bash
pip install -r requirements.txt
Миграции и фикстуры
bash
python manage.py makemigrations
python manage.py migrate
# Импорт групп и фикстур (если есть)
python manage.py loaddata fixtures/groups.json
Создание суперпользователя
bash
python manage.py createsuperuser
Запуск сервера
bash
python manage.py runserver
 Работа с API
В браузере или Postman доступны эндпоинты для работы:

Регистрации, логина (JWT)

CRUD пользователей

CRUD курсов и уроков

Работа с платежами (список, фильтрация)

Примечание: для работы с защищенными эндпоинтами необходимо получить токен JWT и передавать его в заголовке Authorization: Bearer <token>.

 Архитектура проекта
Development vs Production
Аспект	Development	Production
Веб-сервер	Django runserver	Gunicorn + Nginx
База данных	PostgreSQL в Docker	PostgreSQL в Docker
Запуск	docker-compose up	docker-compose -f docker-compose.prod.yml up
Отладка	DEBUG=True	DEBUG=False
Статика	Volume mount	Собрана в образе
Деплой	Вручную	Автоматически через GitHub Actions
Безопасность
Все секретные данные хранятся в GitHub Secrets

Production окружение изолировано в Docker-контейнерах

DEBUG режим отключен в production

Используются environment variables для конфигурации