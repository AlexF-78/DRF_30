from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer


class UserRegistrationAPIView(generics.CreateAPIView):
    """API для регистрации новых пользователей."""

    # Модель пользователя
    queryset = User.objects.all()
    # Сериализатор для регистрации
    serializer_class = UserRegistrationSerializer
    # Доступ разрешен без авторизации
    permission_classes = [permissions.AllowAny]


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """API для просмотра и обновления профиля текущего пользователя."""

    # Сериализатор для профиля
    serializer_class = UserSerializer
    # Требует авторизаци
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Возвращает текущего авторизованного пользователя
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный API-вью для получения JWT токена."""

    # Доступ разрешен без авторизации
    permission_classes = [permissions.AllowAny]
