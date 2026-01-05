from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from posts.models import Like, Post


class LikeBaseTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="user1", email="user1@test.com", password="password123"
        )
        self.other_user = User.objects.create_user(
            username="user2", email="user2@test.com", password="password123"
        )
        self.post = Post.objects.create(author=self.other_user, content="Test post")
        self.like_url = reverse("post-like", args=[self.post.id])
        self.unlike_url = reverse("post-unlike", args=[self.post.id])
        return super().setUp()

    def test_user_can_like_post(self):
        self.client.force_authenticate(self.user)  # type: ignore
        res = self.client.post(self.like_url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)

    def test_anonymous_cant_like(self):
        res = self.client.post(self.like_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Like.objects.count(), 0)

    def test_user_cant_like_twice(self):
        self.client.force_authenticate(self.user)  # type: ignore
        self.client.post(self.like_url)
        res = self.client.post(self.like_url)
        self.assertNotEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)

    def test_user_can_unlike(self):
        self.client.force_authenticate(self.user)  # type: ignore
        self.client.post(self.like_url)
        res = self.client.post(self.unlike_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Like.objects.count(), 0)

    def test_unlike_without_like_fails(self):
        self.client.force_authenticate(self.user)  # type: ignore
        res = self.client.post(self.unlike_url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
