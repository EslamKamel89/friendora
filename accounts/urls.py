from django.urls import URLPattern, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register("users", views.FollowViewSet, basename="users")
urlpatterns: list[URLPattern] = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("profile/me", views.MeProfileView.as_view(), name="my-profile"),
]
urlpatterns += router.urls
