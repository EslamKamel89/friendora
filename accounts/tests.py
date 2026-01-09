from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User


class AuthTests(APITestCase):
    def test_register(self):
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "eslam@0123456789",
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_login(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="eslam@0123456789"
        )
        url = reverse("login")
        data = {
            "username": "testuser",
            "password": "eslam@0123456789",
        }
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.json())
        self.assertIn("refresh", res.json())


def create_temporary_image(name="test_image.jpg", size=(100, 100), format="JPEG"):
    """Generates a temporary image file for tests."""
    image_buffer = BytesIO()
    image = Image.new("RGB", size, "white")
    image.save(image_buffer, format=format)
    image_buffer.seek(0)
    return SimpleUploadedFile(
        name, image_buffer.getvalue(), content_type=f"image/{format.lower()}"
    )


class ProfileUploadTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username="user1",
            email="u1@test.com",
            password="pass12345",
        )
        self.client.force_authenticate(self.user)  # type: ignore
        return super().setUp()

    def test_upload_avatar(self):
        url = reverse("my-profile")
        res = self.client.patch(
            url,
            data={"bio": "test", "avatar": create_temporary_image()},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
