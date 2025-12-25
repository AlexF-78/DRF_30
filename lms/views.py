from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Payment

from .filters import PaymentFilter
from .models import Course, Lesson, Subscription
from .paginators import StandardResultsSetPagination
from .permissions import IsModerator, IsOwnerOrModerator
from .serializers import (CourseSerializer, LessonSerializer,
                          PaymentSerializer, SubscriptionSerializer)


# CRUD для курсов через ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления курсами.
    Предоставляет полный CRUD (создание, чтение, обновление, удаление) для курсов.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Возвращает queryset курсов в зависимости от прав пользователя.
        - Пользователи видят только свои курсы.
        - Модераторы видят все курсы.
        """
        user = self.request.user

        # Модераторы видят все курсы
        if user.groups.filter(name="moderators").exists():
            return Course.objects.prefetch_related("lessons").all()

        # Обычные пользователи видят только свои курсы
        return Course.objects.prefetch_related("lessons").filter(owner_id=user.id)

    def get_permissions(self):
        """
        Настраивает права доступа в зависимости от действия.
        - Только авторизованные пользователи могут создавать и удалять курсы.
        - Модераторы имеют расширенные права.
        """
        if self.action == "create":
            # Создавать могут только авторизованные пользователи (не модераторы)
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action == "destroy":
            # Удалять могут только авторизованные пользователи (не модераторы)
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """
        При создании курса автоматически назначается его владелец - текущий пользователь.
        """
        serializer.save(owner=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Возвращаем только уроки текущего пользователя
        return Lesson.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Сохраняем владельца при создании урока
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    """
    API-эндпоинт для получения списка уроков.
    Пользователи видят только свои уроки, модераторы - все уроки.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Возвращает queryset уроков в зависимости от прав пользователя.
        """
        user = self.request.user

        # Модераторы видят все уроки
        if user.groups.filter(name="moderators").exists():
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
    permission_classes = [
        IsAuthenticated,
        ~IsModerator,
    ]  # Модераторы не могут создавать

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
    serializer_class = LessonSerializer
    permission_classes = [
        IsAuthenticated,
        IsOwnerOrModerator,
    ]  # Модераторы не могут удалять

    def get_permissions(self):
        # Проверяем, что пользователь - владелец (не модератор)
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            # Модераторы не могут удалять
            return [IsAuthenticated()]
        return super().get_permissions()


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


class SubscriptionToggleView(APIView):
    """
    API-эндпоинт для переключения состояния подписки на курс.

    Позволяет пользователю подписаться на курс или отписаться от него.
    Если подписка существует - она удаляется, если нет - создается новая.

    Методы:
    - POST: Переключение состояния подписки для указанного курса
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, course_id=None, *args, **kwargs):
        user = request.user
        course = get_object_or_404(Course, id=course_id)
        subs_qs = Subscription.objects.filter(user=user, course=course)

        if subs_qs.exists():
            # Подписка есть - удаляем
            subs_qs.delete()
            message = "подписка удалена"
        else:
            # Если нет - создаёт
            Subscription.objects.create(user=user, course=course)
            message = "подписка добавлена"

        return Response({"message": message})


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления подписками пользователя.

    Позволяет пользователям:
    - Просматривать свои подписки на курсы
    - Создавать новые подписки
    - Удалять существующие подписки

    При создании проверяет, не существует ли уже подписка на указанный курс.
    Пользователи могут видеть только свои подписки.
    """

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Возвращаем только подписки текущего пользователя
        return Subscription.objects.filter(user=self.request.user)

    # Сохраняем пользователя при создании подписки
    def perform_create(self, serializer):
        # Проверяем, не существует ли уже такая подписка
        user = self.request.user
        course = serializer.validated_data["course"]

        if Subscription.objects.filter(user=user, course=course).exists():
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"detail": "Вы уже подписаны на этот курс"})

        serializer.save(user=self.request.user)
