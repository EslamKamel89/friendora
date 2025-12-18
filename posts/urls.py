from django.urls import URLPattern, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("", views.PostViewSet, basename="post")
urlpatterns: list[URLPattern] = [
    # path("", views.PostListCreateApiView.as_view()),
    # path("<int:pk>/", views.PostRetrieveUpdateDestroyApiView.as_view()),
] + router.urls
