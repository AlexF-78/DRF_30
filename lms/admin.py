from django.contrib import admin

from .models import Course, Lesson, Subscription
from .tasks import send_course_update_notification


# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name", "description"]

    def save_model(self, request, obj, form, change):
        """
        Сохраняет курс в админке и отправляет уведомления при обновлении.

        Args:
            request: HttpRequest объект
            obj: Сохраняемый объект Course
            form: Форма админки
            change: True если объект изменяется, False если создаётся новый
        """
        super().save_model(request, obj, form, change)

        # change=True означает обновление существующего объекта
        if change:
            send_course_update_notification.delay(obj.id)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["name", "course", "video_link"]
    list_filter = ["course"]
    search_fields = ["name", "description", "video_link"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "created_at")
    list_filter = ("course", "created_at")
    search_fields = ("user__email", "course__name")
