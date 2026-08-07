from django import forms
from .models import Course


class CourseForm(forms.ModelForm):

    class Meta:

        model = Course

        fields = [
            "name",
            "teacher",
            "units",
            "difficulty",
            "exam_date",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام درس"}
            ),
            "teacher": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام استاد"}
            ),
            "units": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "difficulty": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 10}
            ),
            "exam_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }
