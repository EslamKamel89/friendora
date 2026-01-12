from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from posts.models import Post, Report
from posts.permissions import IsNotPostOwner, StaffReadOnly
from posts.serializers import ReportCreateSerializer


class ReportViewSet(ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportCreateSerializer
    permission_classes = [IsAuthenticated, StaffReadOnly]

    def perform_create(self, serializer: ReportCreateSerializer):
        post = serializer.validated_data.get("post")  # type: ignore
        permission = IsNotPostOwner()
        if not permission.has_object_permission(self.request, self, post):  # type: ignore
            raise PermissionDenied("You cannot report your own post.")
        serializer.save(reporter=self.request.user)
