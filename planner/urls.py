from django.urls import path

from . import views

app_name = "planner"


urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_session, name="create"),
    path("<int:pk>/edit/", views.update_session, name="update"),
    path("<int:pk>/delete/", views.delete_session, name="delete"),
    path("<int:pk>/complete/", views.complete_session, name="complete"),
]
