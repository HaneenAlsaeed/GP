from django.contrib import admin
from .models import Project, Category, Decision, Comment, Attachment, ActivityLog, FavoriteDecision


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "created_at", "updated_at")
    search_fields = ("title", "owner__username")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "badge_color", "icon_class")
    search_fields = ("name",)


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "project", "category", "risk_level", "priority", "status", "owner")
    list_filter = ("risk_level", "priority", "status", "category")
    search_fields = ("title", "description", "owner__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "decision", "author", "timestamp")
    search_fields = ("text", "author__username")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "decision", "filename", "file_size", "uploaded_by", "uploaded_at")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action_type", "description", "timestamp")
    list_filter = ("action_type", "timestamp")


@admin.register(FavoriteDecision)
class FavoriteDecisionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "decision", "created_at")
