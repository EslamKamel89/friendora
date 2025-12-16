from django.urls import URLPattern
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("", views.PostViewSet, basename="post")
urlpatterns: list[URLPattern] = router.urls
