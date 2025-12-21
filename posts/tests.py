import io
from email import header
from email.mime import multipart

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, force_authenticate

from accounts.models import User
from posts.models import Post


class PostBaseTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username="user1", email="user1@test.com", password="strongpassword123"
        )
        self.other_user = User.objects.create(
            username="user2", email="user2@test.com", password="strongpassword123"
        )
        self.list_url = reverse("post-list")
        return super().setUp()

    def generate_test_image(self):
        file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color="red")
        image.save(file, format="JPEG")
        file.seek(0)
        return SimpleUploadedFile("post.jpg", file.read(), content_type="image/jpeg")


class PostAuthTests(PostBaseTest):
    def test_create_post_require_auth(self):
        data = {"content": "unauthorized post"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostCreateTests(PostBaseTest):
    def test_authenticated_users_can_create_posts(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        data = {"content": "authorized post"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.all().first().author, self.user)  # type: ignore


class PostImageUploadTest(PostBaseTest):
    def test_create_post_with_image(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        image = self.generate_test_image()
        data = {"content": "test post", "image": image}
        response = self.client.post(self.list_url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.all().first().author, self.user)  # type: ignore


class PostPermissionTests(PostBaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.post = Post.objects.create(author=self.user, content="original post")
        self.detail_url = reverse("post-detail", args=[self.post.id])

    def test_owner_can_update_post(self):
        self.client.force_authenticate(user=self.user)  # type: ignore
        res = self.client.patch(self.detail_url, {"content": "updated content"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_non_owner_cant_update_post(self):
        self.client.force_authenticate(user=self.other_user)  # type: ignore
        res = self.client.patch(self.detail_url, {"content": "updated content"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_post(self):
        self.client.force_authenticate(user=self.user)  # type: ignore

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_owner_cannot_delete_post(self):
        self.client.force_authenticate(user=self.other_user)  # type: ignore

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
