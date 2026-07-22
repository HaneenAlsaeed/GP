from django.urls import path
from . import views

urlpatterns = [
    # Page views
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile_view, name="profile"),
    path("following", views.following_view, name="following"),

    # RESTful API Endpoints
    path("api/posts", views.posts_api, name="posts_api"),
    path("api/posts/<int:post_id>", views.post_detail_api, name="post_detail_api"),
    path("api/posts/<int:post_id>/like", views.like_api, name="like_api"),
    path("api/users/<str:username>/follow", views.follow_api, name="follow_api"),
]
