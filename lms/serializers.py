from rest_framework import serializers

from users.models import Payment

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.
    Используется для преобразования объектов уроков в удобный формат JSON и обратно.
    """

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.
    Предназначен для отображения информации о курсе, включая количество уроков и список уроков.
    """

    # Поле для вывода количества уроков, связанных с курсом
    lessons_count = serializers.SerializerMethodField()
    # Поле для вывода списка уроков, связанных с курсом
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "preview",
            "description",
            "lessons_count",
            "lessons",
        )

    def get_lessons_count(self, obj):
        """
        Метод для получения количества уроков, связанных с курсом.
        Используется в качестве источника для поля lessons_count.
        Args:
            obj (Course): объект курса
        Returns:
            int: количество уроков, связанных с курсом
        """
        return obj.lessons.count()


class PaymentSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Payment.
        Используется для отображения информации о платежах, включая связанную информацию о курсе, уроке и пользователе.
        """
    # Поле для отображения имени курса, связанного с платежом
    course_name = serializers.CharField(source="paid_course.name", read_only=True)
    # Поле для отображения имени урока, связанного с платежом
    lesson_name = serializers.CharField(source="paid_lesson.name", read_only=True)
    # Поле для отображения email пользователя, совершившего платеж
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_email",
            "payment_date",
            "paid_course",
            "course_name",
            "paid_lesson",
            "lesson_name",
            "amount",
            "payment_method",
        ]
        read_only_fields = ["payment_date"]
