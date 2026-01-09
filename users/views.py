from django.urls import reverse
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from lms.services import (create_stripe_checkout_session, create_stripe_price,
                          create_stripe_product)

from .models import Payment, User
from .serializers import (PaymentSerializer, UserRegistrationSerializer,
                          UserSerializer)


class UserRegistrationAPIView(generics.CreateAPIView):
    """API для регистрации новых пользователей."""

    # Модель пользователя
    queryset = User.objects.all()
    # Сериализатор для регистрации
    serializer_class = UserRegistrationSerializer
    # Доступ разрешен без авторизации
    permission_classes = [permissions.AllowAny]


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """API для просмотра и обновления профиля текущего пользователя."""

    # Сериализатор для профиля
    serializer_class = UserSerializer
    # Требует авторизаци
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Возвращает текущего авторизованного пользователя
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный API-вью для получения JWT токена."""

    # Доступ разрешен без авторизации
    permission_classes = [permissions.AllowAny]


class PaymentCreateAPIView(generics.CreateAPIView):
    """
    Создание платежа.
    Для способа оплаты 'transfer' создает сессию оплаты в Stripe.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Устанавливаем пользователя из запроса
        payment = serializer.save(user=self.request.user)

        # Если способ оплаты - перевод на счёт, создаем сессию в Stripe
        if payment.payment_method == Payment.PAYMENT_METHOD_TRANSFER:
            try:
                # Определяем продукт (курс или урок)
                if payment.paid_course:
                    product_name = f"Курс: {payment.paid_course.name}"
                    product_description = payment.paid_course.description or ""
                elif payment.paid_lesson:
                    product_name = f"Урок: {payment.paid_lesson.name}"
                    product_description = payment.paid_lesson.description or ""
                    # Если урок принадлежит курсу, добавим это в описание
                    if payment.paid_lesson.course:
                        product_description = f"Курс: {payment.paid_lesson.course.name}. {product_description}"
                else:
                    product_name = f"Payment #{payment.id}"
                    product_description = "Payment for educational content"

                # Создаем продукт в Stripe (получаем ID)
                stripe_product_id = create_stripe_product(
                    product_name, product_description
                )

                # Сумма в копейках (умножаем на 100)
                amount_in_cents = int(payment.amount * 100)

                # Создаем цену в Stripe (получаем ID)
                stripe_price_id = create_stripe_price(
                    stripe_product_id, amount_in_cents, currency="rub"
                )

                # URL для перенаправления после оплаты
                success_url = self.request.build_absolute_uri(
                    reverse("payment-success")
                )
                cancel_url = self.request.build_absolute_uri(reverse("payment-cancel"))

                # Создаем сессию оплаты в Stripe (получаем объект сессии)
                session = create_stripe_checkout_session(
                    stripe_price_id, success_url, cancel_url
                )

                # Сохраняем данные Stripe в модели Payment
                payment.stripe_product_id = stripe_product_id
                payment.stripe_price_id = stripe_price_id
                payment.stripe_session_id = session.id
                payment.stripe_payment_link = session.url
                payment.save()

            except Exception:
                # Игнорируем ошибку Stripe, платеж создается без Stripe данных
                pass


class PaymentSuccessAPIView(APIView):
    """
    Страница успешной оплаты.
    """

    def get(self, request):
        return Response({"message": "Payment successful!"})


class PaymentCancelAPIView(APIView):
    """
    Страница отмены оплаты.
    """

    def get(self, request):
        return Response({"message": "Payment cancelled."})
