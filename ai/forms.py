from django import forms


class AIQuestionForm(forms.Form):

    question = forms.CharField(
        label="سؤال",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "سؤال خود را درباره این نوت بنویسید...",
            }
        ),
    )

    selected_text = forms.CharField(required=False, widget=forms.HiddenInput())
