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

    def clean_units(self):

        units = self.cleaned_data.get("units")

        if units is not None and units < 1:
            raise forms.ValidationError("تعداد واحد باید حداقل ۱ باشد.")

        return units

    def clean_difficulty(self):

        difficulty = self.cleaned_data.get("difficulty")

        if difficulty is not None and not 1 <= difficulty <= 10:
            raise forms.ValidationError("سطح سختی باید بین ۱ تا ۱۰ باشد.")

        return difficulty
