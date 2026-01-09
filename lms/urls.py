# from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import SubscriptionToggleView, SubscriptionViewSet

router = DefaultRouter()
router.register(r"courses", views.CourseViewSet, basename="courses")
router.register(r"subscriptions", SubscriptionViewSet, basename="subscriptions")

urlpatterns = [
    path("", include(router.urls)),
    path("lessons/", views.LessonListAPIView.as_view(), name="lesson-list"),
    path("lessons/create/", views.LessonCreateAPIView.as_view(), name="lesson-create"),
    path(
        "lessons/<int:pk>/",
        views.LessonRetrieveAPIView.as_view(),
        name="lesson-retrieve",
    ),
    path(
        "lessons/<int:pk>/update/",
        views.LessonUpdateAPIView.as_view(),
        name="lesson-update",
    ),
    path(
        "lessons/<int:pk>/delete/",
        views.LessonDestroyAPIView.as_view(),
        name="lesson-delete",
    ),
    path("payments/", views.PaymentListAPIView.as_view(), name="payment-list"),
    path(
        "api/subscription/toggle/",
        SubscriptionToggleView.as_view(),
        name="subscription-toggle",
    ),
]
