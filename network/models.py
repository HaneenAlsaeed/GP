from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Provides utility methods for social graph queries (followers, following, posts).
    """

    def followers_count(self):
        """Returns the number of users following this user."""
        return self.follower_relationships.count()

    def following_count(self):
        """Returns the number of users this user is following."""
        return self.following_relationships.count()

    def posts_count(self):
        """Returns total posts created by this user."""
        return self.posts.count()

    def is_following(self, target_user):
        """Checks if self is following target_user."""
        if not target_user or not target_user.is_authenticated or self == target_user:
            return False
        return self.following_relationships.filter(following=target_user).exists()

    def __str__(self):
        return f"{self.username}"


class Post(models.Model):
    """
    Represents a user post in the network.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def likes_count(self):
        """Returns total likes for this post."""
        return self.likes.count()

    def is_liked_by(self, user):
        """Returns True if the given user has liked this post."""
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()

    def serialize(self, request_user=None):
        """
        Serializes post data into a dictionary suitable for JSON API responses.
        """
        is_liked = False
        is_owner = False
        if request_user and request_user.is_authenticated:
            is_liked = self.likes.filter(user=request_user).exists()
            is_owner = (self.user == request_user)

        return {
            "id": self.id,
            "user": self.user.username,
            "user_id": self.user.id,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d, %Y, %I:%M %p"),
            "iso_timestamp": self.timestamp.isoformat(),
            "likes_count": self.likes.count(),
            "is_liked": is_liked,
            "is_owner": is_owner
        }

    def __str__(self):
        return f"Post {self.id} by {self.user.username} at {self.timestamp}"


class Like(models.Model):
    """
    Represents a like given by a user to a post.
    Ensures a user can like a specific post only once.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"


class Follow(models.Model):
    """
    Represents a follow relationship where follower follows following.
    Prevents self-following and duplicate follow records.
    """
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_relationships")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_relationships")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Users cannot follow themselves.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
