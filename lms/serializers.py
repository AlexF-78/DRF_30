from rest_framework import serializers

from users.models import Payment

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока"""

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса. Выводит и количество уроков, и список уроков."""

    # Поле для вывода количества уроков
    lessons_count = serializers.SerializerMethodField()
    # Поле для вывода списка уроков
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
        """Метод для получения количества уроков в курсе"""
        return obj.lessons.count()


class PaymentSerializer(serializers.ModelSerializer):
    # Дополнительные поля для удобства чтения
    course_name = serializers.CharField(source="paid_course.name", read_only=True)
    lesson_name = serializers.CharField(source="paid_lesson.name", read_only=True)
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
