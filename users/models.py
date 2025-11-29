
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    # Заменяем авторизацию на email
    username = None
    email = models.EmailField(('email address'), unique=True)


    # Дополнительные поля
    phone = models.CharField(('Телефон'), max_length=20, blank=True, null=True)
    city = models.CharField(('Город'), max_length=50, blank=True, null=True)
    avatar = models.ImageField(('Аватар'), upload_to='users/avatars/', blank=True, null=True)

    # Поле для авторизации
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


    def __str__(self):
        return self.email
