from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from accounts.models import Follow, User
from accounts.serializers import FollowSerializer, RegisterSerializer
from common.throttle import FollowThrottle


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class FollowViewSet(GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["POST"], throttle_classes=[FollowThrottle])
    def follow(self, request: Request, pk=None):
        follower: User = request.user
        following: User = self.get_object()

        if follower == following:
            return Response(
                {"detail": "Cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST
            )

        _, created = Follow.objects.get_or_create(
            follower=follower, following=following
        )

        if not created:
            return Response(
                {"detail": "Already following"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"detail": "Followed"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"], throttle_classes=[FollowThrottle])
    def unfollow(self, request: Request, pk=None):
        follower: User = request.user
        following: User = self.get_object()

        if follower == following:
            return Response(
                {"detail": "Cannot unfollow yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted, _ = Follow.objects.filter(
            follower=follower, following=following
        ).delete()

        if deleted == 0:
            return Response(
                {"detail": "Not following"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"detail": "Unfollowed"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def followers(self, request: Request, pk=None):
        user: User = self.get_object()
        qs = user.followers_set.select_related("follower")
        return Response(FollowSerializer(qs, many=True).data)

    @action(detail=True, methods=["GET"])
    def following(self, request: Request, pk=None):
        user: User = self.get_object()
        qs = user.following_set.select_related("following")
        return Response(FollowSerializer(qs, many=True).data)
