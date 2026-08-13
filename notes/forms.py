from django import forms
from .models import Note


class NoteForm(forms.ModelForm):

    class Meta:
        model = Note

        fields = [
            "course",
            "title",
            "content",
        ]

        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "عنوان نوت"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 15,
                    "placeholder": "محتوای نوت را بنویسید...",
                }
            ),
        }
