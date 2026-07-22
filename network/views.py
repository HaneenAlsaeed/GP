import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import User, Post, Like, Follow


@ensure_csrf_cookie
def index(request):
    """
    Main homepage view listing all posts, ordered by newest first, paginated 10 per page.
    Also provides a post creation form for logged-in users.
    """
    posts_list = Post.objects.all().select_related("user").prefetch_related("likes")
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Attach is_liked and is_owner helper attributes for standard server rendering
    for post in page_obj:
        post.is_liked = post.is_liked_by(request.user)
        post.is_owner = (request.user.is_authenticated and post.user == request.user)

    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "page_title": "All Posts",
        "feed_type": "all"
    })


def profile_view(request, username):
    """
    User Profile view showing user metadata (followers, following, post count),
    follow/unfollow toggle button, and all user's posts (paginated 10 per page).
    """
    profile_user = get_object_or_404(User, username=username)
    posts_list = Post.objects.filter(user=profile_user).select_related("user").prefetch_related("likes")
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    for post in page_obj:
        post.is_liked = post.is_liked_by(request.user)
        post.is_owner = (request.user.is_authenticated and post.user == request.user)

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = request.user.is_following(profile_user)

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "is_following": is_following,
        "followers_count": profile_user.followers_count(),
        "following_count": profile_user.following_count(),
        "posts_count": profile_user.posts_count(),
        "page_obj": page_obj,
        "is_self": (request.user == profile_user)
    })


@login_required(login_url="login")
def following_view(request):
    """
    Following feed displaying posts only from users that the current logged-in user follows.
    """
    followed_user_ids = request.user.following_relationships.values_list("following_id", flat=True)
    posts_list = Post.objects.filter(user_id__in=followed_user_ids).select_related("user").prefetch_related("likes")
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    for post in page_obj:
        post.is_liked = post.is_liked_by(request.user)
        post.is_owner = (request.user.is_authenticated and post.user == request.user)

    return render(request, "network/following.html", {
        "page_obj": page_obj,
        "page_title": "Following Feed",
        "feed_type": "following"
    })


def login_view(request):
    """
    Renders login template and handles user authentication.
    """
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    """
    Logs out the active user session.
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
    Renders registration template and processes new user creation.
    """
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirmation = request.POST.get("confirmation", "")

        if not username:
            return render(request, "network/register.html", {
                "message": "Username is required."
            })

        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


# ==========================================
# RESTful API Endpoints
# ==========================================

def posts_api(request):
    """
    API endpoint for retrieving posts (GET) or creating a new post (POST).
    """
    if request.method == "GET":
        feed_type = request.GET.get("feed", "all")
        username = request.GET.get("username", None)
        page_number = request.GET.get("page", 1)

        if feed_type == "profile" and username:
            profile_user = get_object_or_404(User, username=username)
            posts_qs = Post.objects.filter(user=profile_user)
        elif feed_type == "following":
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication required for following feed."}, status=401)
            followed_ids = request.user.following_relationships.values_list("following_id", flat=True)
            posts_qs = Post.objects.filter(user_id__in=followed_ids)
        else:
            posts_qs = Post.objects.all()

        posts_qs = posts_qs.select_related("user").prefetch_related("likes")
        paginator = Paginator(posts_qs, 10)
        page_obj = paginator.get_page(page_number)

        serialized_posts = [post.serialize(request.user) for post in page_obj]

        return JsonResponse({
            "posts": serialized_posts,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "page": page_obj.number,
            "num_pages": paginator.num_pages,
            "total_posts": paginator.count
        })

    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be signed in to create a post."}, status=401)

        try:
            data = json.loads(request.body)
            content = data.get("content", "").strip()
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

        if not content:
            return JsonResponse({"error": "Post content cannot be empty."}, status=400)

        post = Post.objects.create(user=request.user, content=content)
        return JsonResponse({
            "message": "Post created successfully.",
            "post": post.serialize(request.user)
        }, status=201)

    return JsonResponse({"error": "Method not allowed."}, status=405)


def post_detail_api(request, post_id):
    """
    API endpoint for editing a specific post (PUT).
    Only the post author can edit their own post.
    """
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "PUT":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=401)

        if post.user != request.user:
            return JsonResponse({"error": "You are not authorized to edit this post."}, status=403)

        try:
            data = json.loads(request.body)
            content = data.get("content", "").strip()
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        if not content:
            return JsonResponse({"error": "Post content cannot be empty."}, status=400)

        post.content = content
        post.save()

        return JsonResponse({
            "message": "Post updated successfully.",
            "post": post.serialize(request.user)
        })

    return JsonResponse({"error": "Method not allowed."}, status=405)


def like_api(request, post_id):
    """
    API endpoint to toggle like/unlike status on a post (POST).
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be signed in to like posts."}, status=401)

    post = get_object_or_404(Post, pk=post_id)
    like_qs = Like.objects.filter(user=request.user, post=post)

    if like_qs.exists():
        like_qs.delete()
        is_liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        is_liked = True

    return JsonResponse({
        "liked": is_liked,
        "likes_count": post.likes_count()
    })


def follow_api(request, username):
    """
    API endpoint to toggle follow/unfollow status for a target user (POST).
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)

    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return JsonResponse({"error": "You cannot follow yourself."}, status=400)

    follow_qs = Follow.objects.filter(follower=request.user, following=target_user)

    if follow_qs.exists():
        follow_qs.delete()
        is_following = False
    else:
        try:
            Follow.objects.create(follower=request.user, following=target_user)
            is_following = True
        except IntegrityError:
            is_following = True

    return JsonResponse({
        "following": is_following,
        "followers_count": target_user.followers_count(),
        "following_count": target_user.following_count()
    })
