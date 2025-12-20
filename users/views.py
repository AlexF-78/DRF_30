from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer


class UserRegistrationAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Доступно без авторизации


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """Просмотр и обновление профиля пользователя"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Требует авторизации

    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный вью для получения JWT токена"""
    permission_classes = [permissions.AllowAny]  # Доступно без авторизации
