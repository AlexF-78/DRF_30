from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Payment, User

# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["email", "phone", "city", "is_staff"]
    list_filter = ["is_staff", "is_superuser", "city"]
    ordering = ["email"]
    # fieldsets = UserAdmin.fieldsets + (
    #    ("Дополнительная информация", {"fields": ("phone", "city", "avatar")}),
    # )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name", "phone", "city", "avatar")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     ("Дополнительная информация", {"fields": ("phone", "city", "avatar")}),
    # )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "first_name", "last_name", "phone", "city", "avatar"),
        }),
    )
    search_fields = ("email", "first_name", "last_name")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
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
        return obj.user.email

    user_email.short_description = "Пользователь"
    user_email.admin_order_field = "user__email"

    def get_paid_for(self, obj):
        if obj.paid_course:
            return f"Курс: {obj.paid_course.name}"
        elif obj.paid_lesson:
            return f"Урок: {obj.paid_lesson.name}"
        return "Не указано"

    get_paid_for.short_description = "Оплачено за"

    def amount_display(self, obj):
        return f"{obj.amount} руб."

    amount_display.short_description = "Сумма"
    amount_display.admin_order_field = "amount"

    def payment_method_display(self, obj):
        return obj.get_payment_method_display()

    payment_method_display.short_description = "Способ оплаты"

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
