from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AccountLoginView,
    AccountRegisterView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProfileView,
    TravelerViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register("travelers", TravelerViewSet, basename="travelers")

urlpatterns = [
    path("auth/register", AccountRegisterView.as_view(), name="auth-register"),
    path("auth/refresh", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/login", AccountLoginView.as_view(), name="auth-login"),
    path("auth/reset", PasswordResetRequestView.as_view(), name="auth-reset-request"),
    path(
        "auth/reset/confirm",
        PasswordResetConfirmView.as_view(),
        name="auth-reset-confirm",
    ),
    path("profile", ProfileView.as_view(), name="profile"),
    path("", include(router.urls)),
]
