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
    """
    ViewSet для управления курсами.
    Предоставляет полный CRUD (создание, чтение, обновление, удаление) для курсов.
    """
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]

    def get_queryset(self):
        """
        Возвращает queryset курсов в зависимости от прав пользователя.
        - Пользователи видят только свои курсы.
        - Модераторы видят все курсы.
        """
        user = self.request.user

        # Модераторы видят все курсы
        if user.groups.filter(name='moderators').exists():
            return Course.objects.prefetch_related("lessons").all()

        # Обычные пользователи видят только свои курсы
        return Course.objects.prefetch_related("lessons").filter(owner_id=user.id)

    def get_permissions(self):
        """
        Настраивает права доступа в зависимости от действия.
        - Только авторизованные пользователи могут создавать и удалять курсы.
        - Модераторы имеют расширенные права.
        """
        if self.action == 'create':
            # Создавать могут только авторизованные пользователи (не модераторы)
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            # Удалять могут только авторизованные пользователи (не модераторы)
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """
        При создании курса автоматически назначается его владелец - текущий пользователь.
        """
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    """
    API-эндпоинт для получения списка уроков.
    Пользователи видят только свои уроки, модераторы - все уроки.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает queryset уроков в зависимости от прав пользователя.
        """
        user = self.request.user

        # Модераторы видят все уроки
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        # Обычный пользователь видит только свои уроки
        return Lesson.objects.filter(owner_id=user.id)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    API-эндпоинт для получения подробной информации об одном уроке.
    Доступен пользователям, являющимся владельцами урока или модераторам.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]


class LessonCreateAPIView(generics.CreateAPIView):
    """
    API-эндпоинт для создания нового урока.
    Только авторизованные пользователи, не являющиеся модераторами, могут создавать уроки.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]  # Модераторы не могут создавать

    def perform_create(self, serializer):
        """
        При создании урока автоматически назначается его владелец - текущий пользователь.
        """
        serializer.save(owner=self.request.user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    """
    API-эндпоинт для обновления существующего урока.
    Пользователи, являющиеся владельцами урока или модераторы, имеют право редактировать.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    API-эндпоинт для удаления урока.
    Удалять могут только владельцы уроков или модераторы.
    """
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModerator]  # Модераторы не могут удалять


class PaymentListAPIView(generics.ListAPIView):
    """
    API-эндпоинт для получения списка платежей.
    Поддерживает фильтрацию и сортировку.
    - Пользователи видят только свои платежи.
    - Администраторы видят все платежи.
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    # Включение фильтрации и сортировки по указанным полям
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter

    # Поля для сортировки
    ordering_fields = ["payment_date", "amount"]

    def get_queryset(self):
        """
        Возвращает queryset платежей в зависимости от прав пользователя.
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
