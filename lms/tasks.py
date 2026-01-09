from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import Course

User = get_user_model()


@shared_task
def send_course_update_notification(course_id):
    """Отправка уведомлений об обновлении курса подписанным пользователям"""
    try:
        course = Course.objects.get(id=course_id)
        # Получаем всех пользователей, подписанных на этот курс
        subscribed_users = User.objects.filter(subscriptions__course=course)

        if not subscribed_users.exists():
            return f"На курс {course.name} нет подписчиков"

        subject = f"Обновление курса: {course.name}"
        message = f'Добрый день!\n\nКурс "{course.name}" был обновлен.\n\nПроверьте новые материалы по ссылке.'

        for user in subscribed_users:
            if user.email:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

        return f"Уведомления отправлены {subscribed_users.count()} подписчикам курса {course.name}"

    except Course.DoesNotExist:
        return f"Курс с id {course_id} не найден"
    except Exception as e:
        return f"Ошибка при отправке уведомлений: {str(e)}"
