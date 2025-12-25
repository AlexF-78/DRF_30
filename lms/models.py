from django.conf import settings
from django.db import models


# Create your models here.
class Course(models.Model):
    """
    Модель Course представляет учебный курс.
    Атрибуты:
        name (CharField): Название урока
        preview (ImageField): изображение превью курса.
        description (TextField): описание курса.
        owner (ForeignKey): Владелец курса (пользователь).

    Метаданные:
        verbose_name (str): Человеко-читаемое название модели.
        verbose_name_plural (str): Множественное число названия модели.

    """

    name = models.CharField(
        "Название",
        max_length=50,
    )
    preview = models.ImageField(
        "Превью", upload_to="courses/previews/", blank=True, null=True
    )
    description = models.TextField("Описание", blank=True, null=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        related_name="courses",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        """
        Возвращает строковое представление объекта курса.

        Returns:
            str: название курса.
        """
        return self.name


class Lesson(models.Model):
    """
    Модель Lesson представляет урок внутри курса.

    Атрибуты:
        name (CharField): Название урока.
        description (TextField): описание урока.
        preview (ImageField): изображение превью урока.
        video_link (URLField): ссылка на видео урока.
        course (ForeignKey): связь с курсом, которому принадлежит урок.
        owner (ForeignKey): Владелец урока (пользователь).

    Метаданные:
        verbose_name (str): Человеко-читаемое название модели.
        verbose_name_plural (str): Множественное число названия модели.
    """

    name = models.CharField("Название", max_length=50)
    description = models.TextField("Описание", blank=True, null=True)
    preview = models.ImageField(
        "Превью", upload_to="lessons/previews/", blank=True, null=True
    )
    video_link = models.URLField("Ссылка на видео", blank=True, null=True)

    # Связь с курсом - один ко многим
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс",
        related_name="lessons",
        blank=True,
        null=True,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        related_name="lessons",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        """
        Возвращает строковое представление объекта урока.

        Returns:
            str: название урока.
        """
        return self.name


class Subscription(models.Model):
    """
    Модель для представления подписок пользователей на курсы.

    Поля:
    - user: Пользователь, который оформил подписку (ForeignKey на модель пользователя).
    - course: Курс, на который подписан пользователь (ForeignKey на модель курса).
    - created_at: Дата и время создания подписки (автоматически устанавливается при создании).

    Метаданные:
    - unique_together: Гарантирует, что один пользователь может подписаться на один курс только один раз.
    - verbose_name: Человекочитаемое имя модели для единственного числа.
    - verbose_name_plural: Человекочитаемое имя модели для множественного числа.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="subscriptions",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс",
        related_name="subscriptions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user} подписан на {self.course}"
