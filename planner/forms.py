from django import forms

from .models import (
    Availability,
    StudyFeedback,
    StudySession,
)


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
            "course": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "عنوان جلسه مطالعه",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "توضیحات جلسه مطالعه...",
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "start_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "end_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        date = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:

            if end_time <= start_time:
                raise forms.ValidationError("ساعت پایان باید بعد از ساعت شروع باشد.")

        if date and start_time and end_time:

            queryset = StudySession.objects.filter(
                user=self.instance.user if self.instance.pk else None,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )

            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

        return cleaned_data


class AvailabilityForm(forms.ModelForm):

    class Meta:
        model = Availability

        fields = [
            "weekday",
            "start_time",
            "end_time",
            "is_active",
        ]

        widgets = {
            "weekday": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "start_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "end_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

        labels = {
            "weekday": "روز هفته",
            "start_time": "ساعت شروع",
            "end_time": "ساعت پایان",
            "is_active": "فعال",
        }

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:

            if end_time <= start_time:
                raise forms.ValidationError("ساعت پایان باید بعد از ساعت شروع باشد.")

        return cleaned_data


class StudyFeedbackForm(forms.ModelForm):

    class Meta:
        model = StudyFeedback

        fields = [
            "mental_readiness",
            "satisfaction",
            "focus_level",
            "difficulty",
            "notes",
        ]

        widgets = {
            "mental_readiness": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "satisfaction": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "focus_level": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "difficulty": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": ("توضیحات خود را درباره این جلسه بنویسید..."),
                }
            ),
        }

        labels = {
            "mental_readiness": "آمادگی ذهنی",
            "satisfaction": "رضایت",
            "focus_level": "میزان تمرکز",
            "difficulty": "سختی جلسه",
            "notes": "توضیحات",
        }
