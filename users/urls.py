from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (CustomTokenObtainPairView, UserProfileAPIView,
                    UserRegistrationAPIView)

urlpatterns = [
    # Эндпоинты без необходимости авторизации (открытые для всех)
    # Регистрация нового пользователя
    path("register/", UserRegistrationAPIView.as_view(), name="register"),
    # Получение токена (логин)
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Обновление токена по рефрешу
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Верификация токена
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Эндпоинт, требующий авторизацию (доступен только для авторизованных пользователей)
    # Получение профиля текущего пользователя
    path("profile/", UserProfileAPIView.as_view(), name="user_profile"),
]
