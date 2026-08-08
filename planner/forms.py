from django import forms

from .models import StudySession


class StudySessionForm(forms.ModelForm):

    class Meta:

        model = StudySession

        fields = [
            "course",
            "title",
            "description",
            "date",
            "start_time",
            "end_time",
        ]

        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "عنوان جلسه مطالعه"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "توضیحات جلسه مطالعه...",
                }
            ),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "end_time": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:

            if end_time <= start_time:

                raise forms.ValidationError("ساعت پایان باید بعد از ساعت شروع باشد.")

        return cleaned_data
