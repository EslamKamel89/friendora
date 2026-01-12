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
        path(
            "admin-reports/posts/<int:post_id>/summary",
            views.ReportSummaryView.as_view(),
        ),
        path(
            "admin-report/posts/<int:report_id>/moderate",
            views.ReportModerationView.as_view(),
        ),
    ]
    + report_router.urls
    + post_router.urls
)
