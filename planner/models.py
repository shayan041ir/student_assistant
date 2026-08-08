from django.db import models
from django.contrib.auth.models import User
from courses.models import Course


class StudySession(models.Model):

    STATUS_CHOICES = [
        ("planned", "برنامه‌ریزی شده"),
        ("completed", "انجام شده"),
        ("cancelled", "لغو شده"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="study_sessions"
    )

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="study_sessions"
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.title} - {self.course.name}"
