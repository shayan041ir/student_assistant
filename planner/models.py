from django.db import models
from django.contrib.auth.models import User

from courses.models import Course


class StudyPlan(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="study_plans"
    )

    date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class StudySession(models.Model):

    plan = models.ForeignKey(
        StudyPlan,
        on_delete=models.CASCADE,
        related_name="sessions"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="study_sessions"
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )

    completed = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.course.name} - {self.start_time}"


class Feedback(models.Model):

    session = models.OneToOneField(
        StudySession,
        on_delete=models.CASCADE,
        related_name="feedback"
    )

    focus = models.PositiveIntegerField()

    energy = models.PositiveIntegerField()

    satisfaction = models.PositiveIntegerField()

    comment = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Feedback - {self.session}"