from django.urls import URLPattern, path
from rest_framework.routers import DefaultRouter

from posts.views_reports import ReportViewSet

from . import views

post_router = DefaultRouter()
post_router.register("entries", views.PostViewSet, basename="post")
report_router = DefaultRouter()
report_router.register("reports", ReportViewSet, basename="reports")
urlpatterns: list[URLPattern] = (
    [
        # path("", views.PostListCreateApiView.as_view()),
        # path("<int:pk>/", views.PostRetrieveUpdateDestroyApiView.as_view()),
    ]
    + report_router.urls
    + post_router.urls
)
