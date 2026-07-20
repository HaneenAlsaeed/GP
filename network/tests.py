import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Post, Like, Follow


class NetworkModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="alice", password="password123")
        self.user2 = User.objects.create_user(username="bob", password="password123")
        self.post1 = Post.objects.create(user=self.user1, content="Hello from Alice!")

    def test_post_creation_and_attributes(self):
        self.assertEqual(self.post1.user.username, "alice")
        self.assertEqual(self.post1.content, "Hello from Alice!")
        self.assertEqual(self.user1.posts_count(), 1)
        self.assertEqual(self.post1.likes_count(), 0)

    def test_follow_relationship(self):
        Follow.objects.create(follower=self.user2, following=self.user1)
        self.assertTrue(self.user2.is_following(self.user1))
        self.assertFalse(self.user1.is_following(self.user2))
        self.assertEqual(self.user1.followers_count(), 1)
        self.assertEqual(self.user2.following_count(), 1)

    def test_self_follow_prevention(self):
        with self.assertRaises(Exception):
            Follow.objects.create(follower=self.user1, following=self.user1)

    def test_like_relationship(self):
        Like.objects.create(user=self.user2, post=self.post1)
        self.assertEqual(self.post1.likes_count(), 1)
        self.assertTrue(self.post1.is_liked_by(self.user2))
        self.assertFalse(self.post1.is_liked_by(self.user1))


class NetworkAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.alice = User.objects.create_user(username="alice", password="password123")
        self.bob = User.objects.create_user(username="bob", password="password123")
        self.post = Post.objects.create(user=self.alice, content="Alice original post")

    def test_create_post_authenticated(self):
        self.client.login(username="alice", password="password123")
        response = self.client.post(
            reverse("posts_api"),
            data=json.dumps({"content": "New API Post"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["post"]["content"], "New API Post")
        self.assertEqual(Post.objects.count(), 2)

    def test_create_post_unauthenticated(self):
        response = self.client.post(
            reverse("posts_api"),
            data=json.dumps({"content": "Unauth Post"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_create_empty_post_fails(self):
        self.client.login(username="alice", password="password123")
        response = self.client.post(
            reverse("posts_api"),
            data=json.dumps({"content": "   "}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_edit_own_post_success(self):
        self.client.login(username="alice", password="password123")
        response = self.client.put(
            reverse("post_detail_api", kwargs={"post_id": self.post.id}),
            data=json.dumps({"content": "Alice edited post text"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, "Alice edited post text")

    def test_edit_others_post_forbidden(self):
        self.client.login(username="bob", password="password123")
        response = self.client.put(
            reverse("post_detail_api", kwargs={"post_id": self.post.id}),
            data=json.dumps({"content": "Bob trying to edit Alice's post"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, "Alice original post")

    def test_like_unlike_api(self):
        self.client.login(username="bob", password="password123")
        # Like
        res1 = self.client.post(reverse("like_api", kwargs={"post_id": self.post.id}))
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(res1.json()["liked"])
        self.assertEqual(res1.json()["likes_count"], 1)

        # Unlike
        res2 = self.client.post(reverse("like_api", kwargs={"post_id": self.post.id}))
        self.assertEqual(res2.status_code, 200)
        self.assertFalse(res2.json()["liked"])
        self.assertEqual(res2.json()["likes_count"], 0)

    def test_follow_unfollow_api(self):
        self.client.login(username="bob", password="password123")
        # Follow alice
        res1 = self.client.post(reverse("follow_api", kwargs={"username": "alice"}))
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(res1.json()["following"])
        self.assertEqual(res1.json()["followers_count"], 1)

        # Unfollow alice
        res2 = self.client.post(reverse("follow_api", kwargs={"username": "alice"}))
        self.assertEqual(res2.status_code, 200)
        self.assertFalse(res2.json()["following"])
        self.assertEqual(res2.json()["followers_count"], 0)

    def test_self_follow_api_error(self):
        self.client.login(username="alice", password="password123")
        res = self.client.post(reverse("follow_api", kwargs={"username": "alice"}))
        self.assertEqual(res.status_code, 400)


class NetworkPaginationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        for i in range(25):
            Post.objects.create(user=self.user, content=f"Post #{i + 1}")

    def test_pagination_page_1(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        page_obj = response.context["page_obj"]
        self.assertEqual(len(page_obj), 10)
        self.assertTrue(page_obj.has_next())
        self.assertFalse(page_obj.has_previous())

    def test_pagination_page_3(self):
        response = self.client.get(reverse("index") + "?page=3")
        self.assertEqual(response.status_code, 200)
        page_obj = response.context["page_obj"]
        self.assertEqual(len(page_obj), 5)
        self.assertFalse(page_obj.has_next())
        self.assertTrue(page_obj.has_previous())
