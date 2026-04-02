from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from lms.models import Course, Lesson
from lms.serializers import (CourseSerializer, LessonSerializer,
                             PaymentSerializer)
from users.models import Payment

from .filters import PaymentFilter


# CRUD для курсов через ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related("lessons").all()
    serializer_class = CourseSerializer


# CRUD для уроков через Generic-классы


# Получение списка уроков
class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# Получение одного урока
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# Создание урока
class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# Обновление урока
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# Удаление урока
class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()


class PaymentListAPIView(generics.ListAPIView):
    """
    Эндпоинт для вывода списка платежей с фильтрацией и сортировкой
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    # Фильтрация и сортировка
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter

    # Поля для сортировки
    ordering_fields = ["payment_date", "amount"]

    def get_queryset(self):
        """
        Пользователи видят только свои платежи
        Администраторы видят все платежи
        """
        user = self.request.user

        # Базовый queryset
        queryset = Payment.objects.select_related("user", "paid_course", "paid_lesson")

        # Обычные пользователи видят только свои платежи
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        return queryset
