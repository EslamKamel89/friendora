import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import User
from posts.models import Post, Tag


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


class PostTagTests(PostBaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.client.force_authenticate(self.user)  # type: ignore

    def test_create_posts_with_tags(self):
        data = {
            "content": "Post with tags",
            "tags_input": ["django", "backend"],
        }
        res = self.client.post(self.list_url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.first()
        self.assertIsNotNone(post)
        self.assertEqual(post.tags.count(), 2)  # type: ignore
        self.assertTrue(Tag.objects.filter(name="django").exists())

    def test_update_tags_of_post(self):
        post = Post.objects.create(content="test update tag", author=self.user)
        url = reverse("post-detail", args=[post.id])
        res = self.client.patch(url, {"tags_input": ["api", "rest"]})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(post.tags.count(), 2)
        self.assertTrue(Tag.objects.filter(name="api").exists())


class PostFilteringTests(PostBaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.client.force_authenticate(self.user)  # type: ignore
        self.post1 = Post.objects.create(author=self.user, content="django post")
        self.post2 = Post.objects.create(author=self.user, content="drf post")
        tag = Tag.objects.create(name="django")
        self.post1.tags.add(tag)

    def test_filter_post_by_tag(self):
        url = f"{self.list_url}?tags__name=django"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()["results"]), 1)


class PostSearchTest(PostBaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.client.force_authenticate(self.user)  # type: ignore
        Post.objects.create(author=self.user, content="Learning django filters")
        Post.objects.create(author=self.user, content="Just a random post")

    def test_search_posts(self):
        url = f"{self.list_url}?search=django"
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()["results"]), 1)
        self.assertIn("django", res.json()["results"][0]["content"])


class PostPaginationTests(PostBaseTest):
    def setUp(self) -> None:
        super().setUp()
        self.client.force_authenticate(self.user)  # type: ignore
        posts = [
            Post(content=f"Post-{i}", author=self.user, slug=f"post-{i}")
            for i in range(10)
        ]
        Post.objects.bulk_create(posts)

    def test_pagination(self):
        res_page1 = self.client.get(f"{self.list_url}?page=1")
        res_page2 = self.client.get(f"{self.list_url}?page=2")
        self.assertEqual(len(res_page1.json()["results"]), 5)
        self.assertEqual(len(res_page2.json()["results"]), 5)
        self.assertEqual(res_page1.status_code, status.HTTP_200_OK)
        self.assertEqual(res_page2.status_code, status.HTTP_200_OK)
