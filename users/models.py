from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """ Менеджер пользователя, реализующий создание обычных пользователей и суперпользователей."""
    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет пользователя с указанным email и паролем.

        Args:
            email (str): Электронный адрес пользователя, обязательный для входа.
            password (str, optional): Пароль пользователя. Если не указан, устанавливается None.
            **extra_fields: Дополнительные поля модели User.

        Returns:
            User: созданный объект пользователя.

        Raises:
            ValueError: Если email не указан.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя.

        Args:
            email (str): Электронный адрес суперпользователя.
            password (str, optional): Пароль суперпользователя.
            **extra_fields: Дополнительные поля модели User.

        Returns:
            User: созданный объект суперпользователя.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Расширенная модель пользователя, основана на AbstractUser, используется email в качестве логина.

    Атрибуты:
        username (None): исключен, используется email для входа.
        email (EmailField): уникальный адрес электронной почты.
        phone (CharField): номер телефона (опционально).
        city (CharField): город проживания (опционально).
        avatar (ImageField): изображение аватара пользователя (опционально).

    Метаданные:
        verbose_name (str): Название модели в единственном числе.
        verbose_name_plural (str): Название модели во множественном числе.
    """
    # Заменяем авторизацию на email
    username = None
    email = models.EmailField(("email address"), unique=True)

    # Дополнительные поля
    phone = models.CharField(("Телефон"), max_length=20, blank=True, null=True)
    city = models.CharField(("Город"), max_length=50, blank=True, null=True)
    avatar = models.ImageField(
        ("Аватар"), upload_to="users/avatars/", blank=True, null=True
    )

    # Поле для авторизации
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        """
        Возвращает строковое представление пользователя, в данном случае его email.

        Returns:
            str: email пользователя.
        """
        return self.email


class Payment(models.Model):
    """
    Модель для хранения информации о платежах пользователей.

    Атрибуты:
        user (ForeignKey): связь с пользователем, совершившим платеж.
        payment_date (DateTimeField): дата и время платежа.(текущее)
        paid_course (ForeignKey): оплаченный курс (опционально).
        paid_lesson (ForeignKey): оплаченный урок (опционально).
        amount (DecimalField): сумма платежа.
        payment_method (CharField): способ оплаты (наличные или перевод).
    """

    # Выбор способа оплаты
    PAYMENT_METHOD_CASH = "cash"
    PAYMENT_METHOD_TRANSFER = "transfer"
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CASH, "Наличные"),
        (PAYMENT_METHOD_TRANSFER, "Перевод на счёт"),
    ]

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="payments",
    )

    payment_date = models.DateTimeField("Дата оплаты", auto_now_add=True)

    paid_course = models.ForeignKey(
        "lms.Course",  # Импортированная модель из lms
        on_delete=models.SET_NULL,  # при удалении курса, платёж остаётся
        verbose_name="Оплаченный курс",
        related_name="payments",
        blank=True,
        null=True,
    )

    paid_lesson = models.ForeignKey(
        "lms.Lesson",  # Импортированная модель из lms
        on_delete=models.SET_NULL,
        verbose_name="Оплаченный урок",
        related_name="payments",
        blank=True,
        null=True,
    )

    amount = models.DecimalField("Сумма оплаты", max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        "Способ оплаты", max_length=20, choices=PAYMENT_METHOD_CHOICES
    )

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]

    def __str__(self):
        """
        Формирует строковое представление платежа, указывая пользователя, оплаченный курс или урок, сумму и статус.

        Returns:
            str: описание платежа.
        """
        if self.paid_course and self.paid_lesson:
            paid_for = "Ошибка: Указан и курс и урок"
        elif self.paid_course:
            paid_for = f"курс: {self.paid_course.name}"
        elif self.paid_lesson:
            paid_for = f"урок: {self.paid_lesson.name}"
        else:
            paid_for = "Ошибка: ни курс ни урок"

        return f"Платёж {self.id}: {self.user.email} - {paid_for} - {self.amount} руб."
