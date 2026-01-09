from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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
from .tasks import send_course_update_notification


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

    @swagger_auto_schema(
        tags=["Курсы"], operation_description="Получение списка курсов с пагинацией"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Курсы"],
        operation_description="Создание нового курса",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Название курса"
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Описание курса"
                ),
                "preview": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Превью курса (URL изображения)",
                ),
            },
        ),
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

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

    def perform_update(self, serializer):
        """
        Сохраняет обновление курса и запускает асинхронную рассылку уведомлений подписчикам
        """
        course = serializer.save()
        # Запускаем асинхронную задачу для отправки уведомлений
        send_course_update_notification.delay(course.id)
        return course


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        tags=["Уроки"],
        operation_description="Создание нового урока",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "video_link", "course"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Название урока"
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Описание урока"
                ),
                "video_link": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Ссылка на видео урока"
                ),
                "course": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID курса"
                ),
                "preview": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Превью урока (URL изображения)",
                ),
            },
        ),
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

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

    @swagger_auto_schema(
        tags=["Уроки"],
        operation_description="Получение списка уроков с пагинацией",
        manual_parameters=[
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Поле для сортировки (например: name, -created_at)",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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

    @swagger_auto_schema(tags=["Уроки"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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

    @swagger_auto_schema(
        tags=["Уроки"],
        operation_description="Создание нового урока",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "video_link", "course"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Название урока"
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Описание урока"
                ),
                "video_link": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Ссылка на видео урока"
                ),
                "course": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID курса"
                ),
                "preview": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Превью урока (URL изображения)",
                ),
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

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

    @swagger_auto_schema(tags=["Уроки"])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(tags=["Уроки"])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


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

    @swagger_auto_schema(tags=["Уроки"])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

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

    @swagger_auto_schema(
        tags=["Платежи"],
        operation_description="Получение списка платежей с фильтрацией и сортировкой",
        manual_parameters=[
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Поле для сортировки (payment_date, amount)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "payment_method",
                openapi.IN_QUERY,
                description="Метод оплаты (cash, transfer)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "course",
                openapi.IN_QUERY,
                description="ID курса",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "lesson",
                openapi.IN_QUERY,
                description="ID урока",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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

    @swagger_auto_schema(
        tags=["Подписки"],
        operation_description="""
        Переключение подписки на курс.

        Если пользователь не подписан на курс - создается подписка.
        Если уже подписан - подписка удаляется.

        Требуется авторизация. Возвращает статус подписки после переключения.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["course_id"],
            properties={
                "course_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID курса для подписки"
                )
            },
        ),
        responses={
            200: openapi.Response(
                "Успешное переключение подписки",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Сообщение о результате операции",
                        )
                    },
                ),
            ),
            400: openapi.Response("Неверные данные"),
            401: openapi.Response("Пользователь не авторизован"),
            404: openapi.Response("Курс не найден"),
        },
    )
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

    @swagger_auto_schema(tags=["Подписки"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Подписки"],
        operation_description="Создание новой подписки на курс",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["course"],
            properties={
                "course": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID курса для подписки"
                )
            },
        ),
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

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
