from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from posts.models import Post


class ReportPermissionsTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username="user1",
            email="u1@test.com",
            password="pass12345",
        )

        self.client.force_authenticate(self.user)  # type: ignore
        self.post = Post.objects.create(
            author=self.user,
            content="My own post",
        )
        # self.reports_url = reverse("reports-list")
        self.reports_url = "/api/posts/reports/"
        return super().setUp()

    def test_user_cannot_report_his_own_post(self):
        res = self.client.post(
            self.reports_url, {"post": self.post.id, "reason": "reporting my own post"}
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_user_cannot_report_post(self):
        staff = User.objects.create_user(
            username="staff",
            email="staff@test.com",
            password="pass12345",
            is_staff=True,
        )
        self.client.force_authenticate(staff)  # type: ignore
        post = Post.objects.create(
            author=self.user,
            content="User post",
        )
        res = self.client.post(
            self.reports_url, {"post": post.id, "reason": "staff reporting"}
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
