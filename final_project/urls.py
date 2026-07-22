"""
URL configuration for final_project (AI Decision Hub GP).
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from network import views as network_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login", network_views.login_view, name="login"),
    path("logout", network_views.logout_view, name="logout"),
    path("register", network_views.register, name="register"),
    path("", include("decision_hub.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
