from django.db import models
from django.contrib.auth.models import User

from notes.models import Note


class AIHistory(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ai_histories"
    )

    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="ai_histories"
    )

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"