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
        null=True
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
        null=True
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
