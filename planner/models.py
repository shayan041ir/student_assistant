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


class Availability(models.Model):

    WEEKDAY_CHOICES = [
        (0, "شنبه"),
        (1, "یکشنبه"),
        (2, "دوشنبه"),
        (3, "سه‌شنبه"),
        (4, "چهارشنبه"),
        (5, "پنجشنبه"),
        (6, "جمعه"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="availabilities"
    )

    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES)

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["weekday", "start_time"]

    def __str__(self):
        return f"{self.user.username} - {self.get_weekday_display()}"


class StudyFeedback(models.Model):

    session = models.OneToOneField(
        StudySession, on_delete=models.CASCADE, related_name="feedback"
    )

    mental_readiness = models.PositiveSmallIntegerField(
        choices=[
            (1, "خیلی کم"),
            (2, "کم"),
            (3, "متوسط"),
            (4, "خوب"),
            (5, "عالی"),
        ]
    )

    satisfaction = models.PositiveSmallIntegerField(
        choices=[
            (1, "خیلی ناراضی"),
            (2, "ناراضی"),
            (3, "متوسط"),
            (4, "راضی"),
            (5, "خیلی راضی"),
        ]
    )

    focus_level = models.PositiveSmallIntegerField(
        choices=[
            (1, "خیلی کم"),
            (2, "کم"),
            (3, "متوسط"),
            (4, "خوب"),
            (5, "عالی"),
        ]
    )

    difficulty = models.PositiveSmallIntegerField(
        choices=[
            (1, "خیلی آسان"),
            (2, "آسان"),
            (3, "متوسط"),
            (4, "سخت"),
            (5, "خیلی سخت"),
        ]
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback - {self.session.title}"
