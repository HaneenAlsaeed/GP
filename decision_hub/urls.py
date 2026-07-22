from django.urls import path
from . import views

app_name = "decision_hub"

urlpatterns = [
    # Dashboard Overview
    path("", views.dashboard_view, name="dashboard"),

    # Projects Management
    path("projects/", views.projects_list_view, name="projects_list"),
    path("projects/create/", views.project_create_page_view, name="project_create_page"),
    path("projects/<int:project_id>/", views.project_detail_view, name="project_detail"),
    path("projects/<int:project_id>/edit/", views.project_edit_view, name="project_edit"),
    path("projects/<int:project_id>/delete/", views.project_delete_view, name="project_delete"),


    # Decision Management
    path("projects/<int:project_id>/decisions/create/", views.decision_create_view, name="decision_create"),
    path("decisions/<int:decision_id>/", views.decision_detail_view, name="decision_detail"),
    path("decisions/<int:decision_id>/edit/", views.decision_edit_view, name="decision_edit"),
    path("decisions/<int:decision_id>/delete/", views.decision_delete_view, name="decision_delete"),

    # Starred Favorites & Activity Log
    path("favorites/", views.favorites_view, name="favorites"),
    path("activity/", views.activity_log_view, name="activity_log"),

    # User Profile
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),

    # RESTful API Endpoints
    path("api/decisions/", views.api_decisions_list, name="api_decisions_list"),
    path("api/decisions/<int:decision_id>/favorite/", views.api_favorite_toggle, name="api_favorite_toggle"),
    path("api/decisions/<int:decision_id>/comment/", views.api_comment_add, name="api_comment_add"),
    path("api/decisions/<int:decision_id>/attachment/", views.api_attachment_upload, name="api_attachment_upload"),
]
