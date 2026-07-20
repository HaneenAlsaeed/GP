import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Project, Category, Decision, Comment, ActivityLog, FavoriteDecision
from .services import get_dashboard_stats, seed_default_categories

User = get_user_model()


class DecisionHubModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_john", password="password123")
        self.category = Category.objects.create(name="Technical", badge_color="primary")
        self.project = Project.objects.create(
            title="Cloud Migration",
            description="Migrating databases to cloud",
            owner=self.user
        )

    def test_project_creation(self):
        self.assertEqual(self.project.title, "Cloud Migration")
        self.assertEqual(self.project.owner.username, "test_john")
        self.assertEqual(self.project.decisions_count(), 0)

    def test_decision_creation_and_serialization(self):
        decision = Decision.objects.create(
            title="Choose Cloud Provider",
            description="Evaluating AWS vs Azure",
            project=self.project,
            category=self.category,
            owner=self.user,
            risk_level="HIGH",
            priority="URGENT",
            status="REVIEW",
            impact_score=80
        )
        self.assertEqual(self.project.decisions_count(), 1)
        self.assertEqual(self.project.high_risk_count(), 1)

        data = decision.serialize(self.user)
        self.assertEqual(data["title"], "Choose Cloud Provider")
        self.assertEqual(data["category"], "Technical")
        self.assertTrue(data["is_owner"])

    def test_comment_and_favorite(self):
        decision = Decision.objects.create(
            title="Encryption Setup",
            description="Setup AES-256",
            project=self.project,
            owner=self.user
        )
        comment = Comment.objects.create(decision=decision, author=self.user, text="Looks good")
        fav = FavoriteDecision.objects.create(user=self.user, decision=decision)

        self.assertEqual(decision.comments.count(), 1)
        self.assertTrue(decision.is_favorited_by(self.user))


class DecisionHubAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username="owner_user", password="password123")
        self.other_user = User.objects.create_user(username="other_user", password="password123")

        self.project = Project.objects.create(title="Security Audit", owner=self.owner)
        self.cat = Category.objects.create(name="Security")
        self.decision = Decision.objects.create(
            title="Implement OAuth2",
            description="Setup OAuth2 SSO authentication",
            project=self.project,
            category=self.cat,
            owner=self.owner,
            risk_level="HIGH"
        )

    def test_dashboard_login_required(self):
        res = self.client.get(reverse("decision_hub:dashboard"))
        self.assertEqual(res.status_code, 302)  # Redirects to login

    def test_project_access_permission(self):
        self.client.login(username="other_user", password="password123")
        res = self.client.get(reverse("decision_hub:project_detail", kwargs={"project_id": self.project.id}))
        self.assertEqual(res.status_code, 403)  # Forbidden for non-owner

    def test_api_decisions_list_search_and_filter(self):
        self.client.login(username="owner_user", password="password123")

        # Live search query match
        res1 = self.client.get(reverse("decision_hub:api_decisions_list") + "?q=OAuth2")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["count"], 1)

        # Risk filter match
        res2 = self.client.get(reverse("decision_hub:api_decisions_list") + "?risk=HIGH")
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["count"], 1)

        # Risk filter mismatch
        res3 = self.client.get(reverse("decision_hub:api_decisions_list") + "?risk=LOW")
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["count"], 0)

    def test_api_favorite_toggle(self):
        self.client.login(username="owner_user", password="password123")

        # Star
        res1 = self.client.post(reverse("decision_hub:api_favorite_toggle", kwargs={"decision_id": self.decision.id}))
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(res1.json()["is_favorite"])

        # Unstar
        res2 = self.client.post(reverse("decision_hub:api_favorite_toggle", kwargs={"decision_id": self.decision.id}))
        self.assertEqual(res2.status_code, 200)
        self.assertFalse(res2.json()["is_favorite"])

    def test_api_comment_add(self):
        self.client.login(username="owner_user", password="password123")
        res = self.client.post(
            reverse("decision_hub:api_comment_add", kwargs={"decision_id": self.decision.id}),
            data=json.dumps({"text": "Critical authentication component."}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["comment"]["text"], "Critical authentication component.")


class DashboardServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="analytics_user", password="password123")
        self.project = Project.objects.create(title="P1", owner=self.user)
        Decision.objects.create(title="D1", project=self.project, owner=self.user, risk_level="CRITICAL", status="DRAFT")
        Decision.objects.create(title="D2", project=self.project, owner=self.user, risk_level="LOW", status="APPROVED")

    def test_stats_aggregator(self):
        stats = get_dashboard_stats(self.user)
        self.assertEqual(stats["total_projects"], 1)
        self.assertEqual(stats["total_decisions"], 2)
        self.assertEqual(stats["high_risk_decisions"], 1)
        self.assertEqual(stats["pending_decisions"], 1)
