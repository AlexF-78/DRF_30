from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Payment, User



# Регистрация модели User с кастомным админским интерфейсом
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Админский интерфейс для управления пользователями.
    Расширяет стандартный UserAdmin, добавляя дополнительные поля и настройки.
    """
    model = User
    list_display = ["email", "phone", "city", "is_staff"]
    list_filter = ["is_staff", "is_superuser", "city"]
    ordering = ["email"]
    # Описание полей, отображаемых при редактировании пользователя
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name", "phone", "city", "avatar")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    # Поля для добавления нового пользователя
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "first_name", "last_name", "phone", "city", "avatar"),
        }),
    )
    # Поля для поиска по списку пользователей
    search_fields = ("email", "first_name", "last_name")


# Регистрация модели Payment с кастомным административным интерфейсом
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Админский интерфейс для управления платежами.
    Включает кастомные отображения и фильтры.
    """
    list_display = (
        "id",
        "user_email",
        "payment_date",
        "get_paid_for",
        "amount_display",
        "payment_method_display",
    )
    list_filter = ("payment_method", "payment_date", "user")
    search_fields = ("user__email", "paid_course__name", "paid_lesson__name")
    readonly_fields = ("payment_date",)
    date_hierarchy = "payment_date"
    list_per_page = 20

    def user_email(self, obj):
        """
        Возвращает email пользователя, связанного с платежом.
        """
        return obj.user.email

    user_email.short_description = "Пользователь"
    user_email.admin_order_field = "user__email"

    def get_paid_for(self, obj):
        """
        Возвращает строку с информацией о том, за что был проведен платеж.
        Если оплачен курс - выводит его название.
        Если урок - его название.
        Если ничего не указано - "Не указано".
        """
        if obj.paid_course:
            return f"Курс: {obj.paid_course.name}"
        elif obj.paid_lesson:
            return f"Урок: {obj.paid_lesson.name}"
        return "Не указано"

    get_paid_for.short_description = "Оплачено за"

    def amount_display(self, obj):
        """
        Форматирует сумму платежа для отображения.
        """
        return f"{obj.amount} руб."

    amount_display.short_description = "Сумма"
    amount_display.admin_order_field = "amount"

    def payment_method_display(self, obj):
        """
        Возвращает отображение метода оплаты.
        """
        return obj.get_payment_method_display()

    payment_method_display.short_description = "Способ оплаты"

    # Поля, отображаемые при просмотре/редактировании платежа
    fieldsets = (
        (
            "Основная информация",
            {"fields": ("user", "payment_date", "amount", "payment_method")},
        ),
        (
            "Оплаченный продукт",
            {
                "fields": ("paid_course", "paid_lesson"),
                "description": "Укажите либо курс, либо урок",
            },
        ),
    )
