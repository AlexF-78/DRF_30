from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User, Payment


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    Обеспечивает валидацию паролей и сбор необходимых данных.
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "phone",
            "city",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        """
        Проверяет совпадение паролей.
        """
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        """
        Создает нового пользователя после успешной валидации.
        """
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о пользователе.
    Используется при получении данных о существующем пользователе.
    """

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "city", "avatar")
        read_only_fields = ("id", "email")


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения платежей.
    """

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "payment_date",
            "stripe_product_id",
            "stripe_price_id",
            "stripe_session_id",
            "stripe_payment_link",
        ]

    def validate(self, data):
        """
        Проверяем, что указан либо курс, либо урок (но не оба одновременно),
        и что сумма положительная.
        """
        # Получаем данные (уже валидированные частично)
        paid_course = data.get("paid_course")
        paid_lesson = data.get("paid_lesson")
        amount = data.get("amount")

        # Проверяем, что указан либо курс, либо урок
        if not paid_course and not paid_lesson:
            raise serializers.ValidationError(
                "Укажите либо курс, либо урок для оплаты."
            )

        # Проверяем, что не указаны оба одновременно
        if paid_course and paid_lesson:
            raise serializers.ValidationError(
                "Укажите только курс ИЛИ только урок, не оба одновременно."
            )

        # Проверяем, что сумма положительная
        if amount is not None and amount <= 0:
            raise serializers.ValidationError("Сумма оплаты должна быть положительной.")

        return data


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания платежа (без полей Stripe, они заполнятся автоматически).
    """

    class Meta:
        model = Payment
        fields = ["paid_course", "paid_lesson", "amount", "payment_method"]

        # Поле user будет устанавливаться автоматически из request.user

    def validate(self, data):
        """
        Проверяем, что указан либо курс, либо урок (но не оба одновременно),
        и что сумма положительная.
        """
        if not data.get("paid_course") and not data.get("paid_lesson"):
            raise serializers.ValidationError(
                "Укажите либо курс, либо урок для оплаты."
            )

        if data.get("paid_course") and data.get("paid_lesson"):
            raise serializers.ValidationError(
                "Укажите только курс ИЛИ только урок, не оба одновременно."
            )

        if data["amount"] <= 0:
            raise serializers.ValidationError("Сумма оплаты должна быть положительной.")

        return data
