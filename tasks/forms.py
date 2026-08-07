from django import forms
from .models import Task


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task

        fields = [
            "course",
            "title",
            "description",
            "due_date",
            "status",
        ]

        widgets = {
            "course": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "عنوان تکلیف"
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "توضیحات تکلیف..."
                }
            ),

            "due_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),
        }
