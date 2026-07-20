from django.contrib import admin
from .models import User, Post, Like, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "date_joined", "is_staff")
    search_fields = ("username", "email")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "short_content", "timestamp", "likes_count")
    search_fields = ("user__username", "content")
    list_filter = ("timestamp",)

    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    short_content.short_description = "Content"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "timestamp")
    search_fields = ("user__username", "post__id")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "timestamp")
    search_fields = ("follower__username", "following__username")
