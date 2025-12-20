from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from lms.models import Course, Lesson
from lms.permissions import IsModerator, IsOwnerOrModerator
from lms.serializers import (CourseSerializer, LessonSerializer,
                             PaymentSerializer)
from users.models import Payment

from .filters import PaymentFilter


# CRUD для курсов через ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    # queryset = Course.objects.prefetch_related("lessons").all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]

    def get_queryset(self):
        """Пользователи видят только свои курсы, модераторы видят все"""
        user = self.request.user

        # Модераторы видят все курсы
        if user.groups.filter(name='moderators').exists():
            return Course.objects.prefetch_related("lessons").all()

        # Обычные пользователи видят только свои курсы
        return Course.objects.prefetch_related("lessons").filter(owner_id=user.id)

    def get_permissions(self):
        """Разграничение прав для разных действий"""
        if self.action == 'create':  # Создавать могут только авторизованные пользователи (не модераторы)
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            # Удалять могут только авторизованные пользователи (не модераторы)
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """При создании курса назначаем владельца"""
        serializer.save(owner=self.request.user)


# CRUD для уроков через Generic-классы


# Получение списка уроков
class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Пользователи видят только свои уроки, модераторы видят всё"""
        user = self.request.user

        # Модераторы видят все уроки
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        # Обычный пользователь видит только свои уроки
        return Lesson.objects.filter(owner_id=user.id)


# Получение одного урока
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]


# Создание урока
class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]  # Модераторы не могут создавать

    def perform_create(self, serializer):
        """При создании урока назначаем владельца"""
        serializer.save(owner=self.request.user)


# Обновление урока
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]


# Удаление урока
class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModerator]  # Модераторы не могут удалять


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
