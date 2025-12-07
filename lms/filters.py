import django_filters

from users.models import Payment


class PaymentFilter(django_filters.FilterSet):
    # Для фильтрации по курсу (по ID)
    paid_course = django_filters.NumberFilter(
        field_name="paid_course__id", label="ID курса"
    )

    # Для фильтрации по уроку (по ID)
    paid_lesson = django_filters.NumberFilter(
        field_name="paid_lesson__id", label="ID урока"
    )

    # Для фильтрации по способу оплаты
    payment_method = django_filters.ChoiceFilter(
        choices=Payment.PAYMENT_METHOD_CHOICES, label="Способ оплаты"
    )

    class Meta:
        model = Payment
        fields = ["paid_course", "paid_lesson", "payment_method"]
