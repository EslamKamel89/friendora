from django.test import TestCase
from django.urls import reverse
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
