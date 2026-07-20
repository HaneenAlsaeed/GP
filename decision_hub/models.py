import os
from django.conf import settings
from django.db import models


class Project(models.Model):
    """
    Represents an organizational project workspace that groups related decisions.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hub_projects"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def decisions_count(self):
        return self.decisions.count()

    def high_risk_count(self):
        return self.decisions.filter(risk_level__in=["HIGH", "CRITICAL"]).count()

    def __str__(self):
        return f"{self.title} (Owner: {self.owner.username})"


class Category(models.Model):
    """
    Decision categories (e.g. Financial, Technical, Operational, Strategic, Legal, Marketing).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    badge_color = models.CharField(max_length=50, default="primary")
    icon_class = models.CharField(max_length=100, default="bi-folder2")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Decision(models.Model):
    """
    Represents a business decision under analysis and evaluation.
    """
    RISK_CHOICES = [
        ("LOW", "Low Risk"),
        ("MEDIUM", "Medium Risk"),
        ("HIGH", "High Risk"),
        ("CRITICAL", "Critical Risk"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low Priority"),
        ("MEDIUM", "Medium Priority"),
        ("HIGH", "High Priority"),
        ("URGENT", "Urgent Priority"),
    ]

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("REVIEW", "Under Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("IMPLEMENTED", "Implemented"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="decisions"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decisions"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hub_decisions"
    )

    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default="MEDIUM")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="MEDIUM")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")

    impact_score = models.IntegerField(default=50)  # 1 to 100
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def is_favorited_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.favorited_by.filter(user=user).exists()

    def serialize(self, request_user=None):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "project_id": self.project.id,
            "project_title": self.project.title,
            "category": self.category.name if self.category else "Uncategorized",
            "category_color": self.category.badge_color if self.category else "secondary",
            "category_icon": self.category.icon_class if self.category else "bi-folder",
            "risk_level": self.risk_level,
            "risk_display": self.get_risk_level_display(),
            "priority": self.priority,
            "priority_display": self.get_priority_display(),
            "status": self.status,
            "status_display": self.get_status_display(),
            "owner": self.owner.username,
            "is_owner": (self.owner == request_user) if request_user and request_user.is_authenticated else False,
            "is_favorite": self.is_favorited_by(request_user),
            "created_at": self.created_at.strftime("%b %d, %Y, %I:%M %p"),
            "updated_at": self.updated_at.strftime("%b %d, %Y, %I:%M %p"),
            "comments_count": self.comments.count(),
            "attachments_count": self.attachments.count()
        }

    def __str__(self):
        return f"[{self.risk_level}] {self.title} - {self.project.title}"


class Comment(models.Model):
    """
    Discussions and audit notes attached to a decision.
    """
    decision = models.ForeignKey(
        Decision,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hub_comments"
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "author_initial": self.author.username[0].upper() if self.author.username else "U",
            "text": self.text,
            "timestamp": self.timestamp.strftime("%b %d, %Y, %I:%M %p"),
            "iso_timestamp": self.timestamp.isoformat()
        }

    def __str__(self):
        return f"Comment by {self.author.username} on Decision {self.decision.id}"


class Attachment(models.Model):
    """
    Uploaded PDF, image, or document attachments for decision evaluation.
    """
    decision = models.ForeignKey(
        Decision,
        on_delete=models.CASCADE,
        related_name="attachments"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hub_attachments"
    )
    file = models.FileField(upload_to="decision_attachments/")
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0)  # Size in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def is_image(self):
        ext = os.path.splitext(self.filename)[1].lower()
        return ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]

    def is_pdf(self):
        ext = os.path.splitext(self.filename)[1].lower()
        return ext == ".pdf"

    def __str__(self):
        return f"{self.filename} for Decision {self.decision.id}"


class ActivityLog(models.Model):
    """
    Audit timeline recording user actions (Decision Created, Edited, Commented, Uploaded).
    """
    ACTION_CHOICES = [
        ("CREATE_PROJECT", "Created Project"),
        ("CREATE_DECISION", "Created Decision"),
        ("EDIT_DECISION", "Edited Decision"),
        ("DELETE_DECISION", "Deleted Decision"),
        ("ADD_COMMENT", "Added Comment"),
        ("UPLOAD_ATTACHMENT", "Uploaded Attachment"),
        ("FAVORITE_TOGGLE", "Toggled Favorite"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hub_activities"
    )
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    decision = models.ForeignKey(
        Decision,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="activity_logs"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="activity_logs"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.username} - {self.action_type} at {self.timestamp}"


class FavoriteDecision(models.Model):
    """
    Bookmarks/Starred decisions for quick access by users.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    decision = models.ForeignKey(
        Decision,
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "decision")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} starred {self.decision.title}"
