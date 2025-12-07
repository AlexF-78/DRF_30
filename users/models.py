from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
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
        return self.email


class Payment(models.Model):
    """Модель для хранения информации о платежах"""

    # Выбор способа оплаты
    PAYMENT_METHOD_CASH = "cash"
    PAYMENT_METHOD_TRANSFER = "transfer"
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CASH, "Наличные"),
        (PAYMENT_METHOD_TRANSFER, "Перевод на счёт"),
    ]

    # ссылка на пользователя
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="payments",
    )

    # Дата оплаты (автоматически текущая дата)
    payment_date = models.DateTimeField("Дата оплаты", auto_now_add=True)

    # ссылка на курс (может быть пустой)
    paid_course = models.ForeignKey(
        "lms.Course",  # Импортированная модель из lms
        on_delete=models.SET_NULL,  # при удалении курса, платёж остаётся
        verbose_name="Оплаченный курс",
        related_name="payments",
        blank=True,
        null=True,
    )

    # Ссылка на урок (может быть пустой)
    paid_lesson = models.ForeignKey(
        "lms.Lesson",  # Импортированная модель из lms
        on_delete=models.SET_NULL,
        verbose_name="Оплаченный урок",
        related_name="payments",
        blank=True,
        null=True,
    )

    # Сумма оплаты
    amount = models.DecimalField("Сумма оплаты", max_digits=10, decimal_places=2)

    # Способ оплаты
    payment_method = models.CharField(
        "Способ оплаты", max_length=20, choices=PAYMENT_METHOD_CHOICES
    )

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]

    def __str__(self):
        if self.paid_course and self.paid_lesson:
            paid_for = "Ошибка: Указан и курс и урок"
        elif self.paid_course:
            paid_for = f"курс: {self.paid_course.name}"
        elif self.paid_lesson:
            paid_for = f"урок: {self.paid_lesson.name}"
        else:
            paid_for = "Ошибка: ни курс ни урок"

        return f"Платёж {self.id}: {self.user.email} - {paid_for} - {self.amount} руб."
