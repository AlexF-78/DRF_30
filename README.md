Django REST API
Описание проекта
Данный проект — образовательная платформа, реализованная на базе Django и Django REST Framework (DRF). 
В нем реализованы модели пользователей, курсов, уроков,
а также система платежей и разграничение доступа на основе ролей (пользователь, модератор).
Проект включает CRUD-операции, фильтрацию данных, авторизацию с помощью JWT и контроль доступа.

Структура проекта
users — приложение для управления пользователями и платежами
lms (или materials) — приложение для управления курсами и уроками
В проекте используются сериализаторы, ViewSet и Generics для CRUD-операций.

В проекте подключен Django REST Framework, настроена JWT-авторизация, реализованы эндпоинты для регистрации,
авторизации и управления пользователями (CRUD, регистрация, авторизация через JWT)

Модели:
Пользователь (замена стандартной аутентификации на email, телефон, город, аватарка)
Курс (название, превью, описание)
Урок (название, описание, превью, ссылка на видео)
Связь между курсами и уроками — один курс содержит много уроков
В приложении users реализована модель Платежи:
Пользователь
Дата оплаты
Оплаченный курс или урок (ссылки на модели)
Сумма оплаты
Способ оплаты (наличные, перевод)
Для моделей реализованы простейшие сериализаторы и CRUD-операции с помощью Viewsets и Generics
Работа API проверена через Postman

В сериализатор модели курса добавлено поле количества уроков (SerializerMethodField)
Реализована модель Платежи с фикстурами для заполнения данных
В сериализаторе курса добавлено поле со списком уроков и количеством уроков курса

Настроена фильтрация и сортировка списка платежей:
Порядок сортировки по дате оплаты
Фильтр по курсу, уроку
Фильтр по способу оплаты
Продвинутый уровень (авторизация и разграничение доступа)
Реализована JWT-аутентификация
Созданы группы: пользователь, модератор
Для модераторов задан ограниченный доступ (может редактировать, просматривать, но не создавать и не удалять курсы/уроки)
Пользователи могут редактировать только свои курсы и уроки
В permissions.py реализованы кастомные права: IsModerator, IsOwner
Контроллеры настроены на разное право доступа посредством метода get_permissions()
Настройка и запуск проекта
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
Примечание: для работы с защищенными эндпоинтами необходимо получить токен JWT
и передавать его в заголовке Authorization: Bearer <token>.

## Запуск с помощью Docker Compose

### Предварительные требования
- Установленный Docker и Docker Compose
- Файл `.env` с переменными окружения (на основе `.env.sample`)

### Запуск проекта
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
Структура сервисов
web: Django приложение на порту 8000

db: PostgreSQL на порту 5433 (внешнем), 5432 (внутреннем)

redis: Redis на порту 6379

celery: Celery worker

celery_beat: Celery beat scheduler



##  Деплой на продакшен сервер

### Настройка сервера (Ubuntu 24.04)

1. **Обновление системы и установка базовых пакетов:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib git curl
Установка Poetry:

bash
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
Настройка PostgreSQL:

bash
sudo -u postgres psql
CREATE DATABASE drf_30_db;
ALTER USER postgres WITH PASSWORD 'your_password';
\q
Клонирование проекта:

bash
cd ~
mkdir -p projects
cd projects
git clone https://github.com/AlexF-78/DRF_30.git
cd DRF_30
Настройка окружения:

bash
cp .env.sample .env
# Отредактируйте .env файл с настройками для продакшена
Установка зависимостей:

bash
poetry install --no-root
poetry shell
Настройка базы данных:

bash
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
Настройка Gunicorn как systemd сервиса:

bash
sudo nano /etc/systemd/system/gunicorn.service
Содержимое файла:

ini
[Unit]
Description=gunicorn daemon for DRF project
After=network.target postgresql.service

[Service]
User=ваш_пользователь
Group=www-data
WorkingDirectory=/home/ваш_пользователь/projects/DRF_30
UMask=007
Environment="PATH=/home/ваш_пользователь/.cache/pypoetry/virtualenvs/drf-30-*/bin"
ExecStart=/home/ваш_пользователь/.cache/pypoetry/virtualenvs/drf-30-*/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/ваш_пользователь/projects/DRF_30/gunicorn.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
Настройка NGINX:

bash
sudo nano /etc/nginx/sites-available/drf_project
Содержимое файла:

nginx
server {
    listen 80;
    server_name ваш_домен_или_ip;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/ваш_пользователь/static/;
    }

    location /media/ {
        alias /home/ваш_пользователь/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ваш_пользователь/projects/DRF_30/gunicorn.sock;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
Запуск сервисов:

bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl restart nginx
 CI/CD с GitHub Actions
Проект настроен с автоматическим CI/CD пайплайном через GitHub Actions.

Workflow файл: .github/workflows/django.yml
При каждом push в ветки develop или feature/homework_34_2:

Запускаются автоматические тесты с Python 3.12

Проверяются миграции базы данных

Запускается покрытие кода (coverage)

Происходит автоматический деплой на продакшен сервер

Настроенные Secrets в GitHub:
SERVER_HOST - IP адрес сервера

SERVER_USER - имя пользователя на сервере

SERVER_PORT - порт SSH (22)

SSH_PRIVATE_KEY - приватный SSH ключ

SECRET_KEY - секретный ключ Django

DATABASE_URL - строка подключения к БД

STRIPE_API_KEY, STRIPE_PUBLIC_KEY - ключи Stripe

Статус CI/CD:
https://github.com/AlexF-78/DRF_30/actions/workflows/django.yml/badge.svg

Проверка работоспособности
После деплоя проверьте:

Основной endpoint: http://ваш_сервер_ip/

Админ панель: http://ваш_сервер_ip/admin/

Статус сервисов: sudo systemctl status gunicorn nginx postgresql
