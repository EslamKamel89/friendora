from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from common.throttle import LikeThrottle
from posts.models import Like, Post, Report
from posts.permissions import IsAuthenticatedForUnsafeMethods, IsOwnerOrReadonly
from posts.serializers import PostSerializer, ReportSummarySerializer
from posts.types import ReportSummaryInput


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().prefetch_related("tags")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedForUnsafeMethods, IsOwnerOrReadonly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tags__name"]
    search_fields = ["content", "slug", "author__username"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        permission_classes=[IsAuthenticated],
        methods=["POST"],
        throttle_classes=[LikeThrottle],
    )
    def like(self, request: Request, pk=None):
        post: Post = self.get_object()
        user = request.user
        like_object, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            return Response(
                {"detail": "Already liked"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"detail": "Liked"}, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        permission_classes=[IsAuthenticated],
        methods=["POST"],
        throttle_classes=[LikeThrottle],
    )
    def unlike(self, request: Request, pk=None):
        post: Post = self.get_object()
        user = request.user
        deleted, _ = Like.objects.filter(user=user, post=post).delete()
        if deleted == 0:
            return Response(
                {"detail": "Not liked yet"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"detail": "Unliked"}, status=status.HTTP_200_OK)


class PostListCreateApiView(GenericAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        posts = self.get_queryset()
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostRetrieveUpdateDestroyApiView(GenericAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadonly]

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(post)
        return Response(serializer.data)

    def put(self, request: Request, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request: Request, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReportSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, post_id: int):
        post = get_object_or_404(Post, pk=post_id)
        reports = Report.objects.filter(post=post, status=Report.Status.PENDING)
        data: ReportSummaryInput = {
            "post": post,
            "post_id": post.id,
            "post_author": post.author.username,
            "post_content": post.content,
            "reports": reports,
        }
        serializer = ReportSummarySerializer(data)
        return Response(serializer.data)
