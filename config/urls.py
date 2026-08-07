from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("admin/", admin.site.urls),

    path("accounts/", include("accounts.urls")),
    path("courses/", include("courses.urls")),
    path("notes/", include("notes.urls")),
    path("tasks/", include("tasks.urls")),
    path("planner/", include("planner.urls")),
    path("ai/", include("ai.urls")),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login"
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout"
    ),
]