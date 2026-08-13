from django.urls import path

from . import views


app_name = "ai"


urlpatterns = [

    path(
        "note/<int:note_id>/ask/",
        views.ask_note,
        name="ask_note",
    ),

    path(
        "note/<int:note_id>/summarize/",
        views.summarize_note,
        name="summarize_note",
    ),

]