from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Follow, User
from posts.models import Like, Post


class TestFollower(APITestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(
            username="user1", email="u1@test.com", password="password123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="u2@test.com", password="password123"
        )

        self.follow_url = reverse("users-follow", args=[self.user2.id])
        self.unfollow_url = reverse("users-unfollow", args=[self.user2.id])
        self.followers_url = reverse("users-followers", args=[self.user2.id])
        self.following_url = reverse("users-following", args=[self.user1.id])
        return super().setUp()

    def test_user_can_follow(self):
        self.client.force_authenticate(self.user1)  # type: ignore
        res = self.client.post(self.follow_url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.count(), 1)

    def test_user_cannot_follow_self(self):
        self.client.force_authenticate(self.user2)  # type: ignore
        res = self.client.post(self.follow_url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Follow.objects.count(), 0)

    def test_duplicate_follow_fails(self):
        self.client.force_authenticate(self.user1)  # type: ignore
        self.client.post(self.follow_url)
        res = self.client.post(self.follow_url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Follow.objects.count(), 1)

    def test_follower_list(self):
        self.client.force_authenticate(self.user1)  # type: ignore
        self.client.post(self.follow_url)
        res = self.client.get(self.followers_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 1)
        self.assertEqual(res.json()[0]["follower_username"], "user1")

    def test_following_list(self):
        self.client.force_authenticate(self.user1)  # type: ignore
        self.client.post(self.follow_url)
        res = self.client.get(self.following_url)
        self.assertEqual(len(res.json()), 1)
        self.assertEqual(res.json()[0]["following_username"], "user2")

    def test_anonymous_cannot_follow(self):
        res = self.client.post(self.follow_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
