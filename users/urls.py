from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (CustomTokenObtainPairView, UserProfileAPIView,
                    UserRegistrationAPIView)

urlpatterns = [
    # Эндпоинты доступные без авторизации
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Эндпоинты требующие авторизации
    path('profile/', UserProfileAPIView.as_view(), name='user_profile'),
]
