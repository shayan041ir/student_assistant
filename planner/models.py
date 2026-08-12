from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from courses.models import Course


class StudySession(models.Model):

    STATUS_CHOICES = [
        ("planned", "برنامه‌ریزی شده"),
        ("completed", "انجام شده"),
        ("cancelled", "لغو شده"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="study_sessions",
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="study_sessions",
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "date",
            "start_time",
        ]

    def __str__(self):
        return f"{self.title} - {self.course.name}"

    @property
    def duration_minutes(self):
        start = self.start_time.hour * 60 + self.start_time.minute

        end = self.end_time.hour * 60 + self.end_time.minute

        return max(
            0,
            end - start,
        )


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
        User,
        on_delete=models.CASCADE,
        related_name="availabilities",
    )

    weekday = models.PositiveSmallIntegerField(
        choices=WEEKDAY_CHOICES,
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "weekday",
            "start_time",
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.get_weekday_display()} "
            f"{self.start_time} - {self.end_time}"
        )

    @property
    def duration_minutes(self):
        start = self.start_time.hour * 60 + self.start_time.minute

        end = self.end_time.hour * 60 + self.end_time.minute

        return max(
            0,
            end - start,
        )


class StudyFeedback(models.Model):

    SCORE_CHOICES = [
        (1, "خیلی کم"),
        (2, "کم"),
        (3, "متوسط"),
        (4, "خوب"),
        (5, "عالی"),
    ]

    SATISFACTION_CHOICES = [
        (1, "خیلی ناراضی"),
        (2, "ناراضی"),
        (3, "متوسط"),
        (4, "راضی"),
        (5, "خیلی راضی"),
    ]

    DIFFICULTY_CHOICES = [
        (1, "خیلی آسان"),
        (2, "آسان"),
        (3, "متوسط"),
        (4, "سخت"),
        (5, "خیلی سخت"),
    ]

    session = models.OneToOneField(
        StudySession,
        on_delete=models.CASCADE,
        related_name="feedback",
    )

    mental_readiness = models.PositiveSmallIntegerField(
        choices=SCORE_CHOICES,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    satisfaction = models.PositiveSmallIntegerField(
        choices=SATISFACTION_CHOICES,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    focus_level = models.PositiveSmallIntegerField(
        choices=SCORE_CHOICES,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    difficulty = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_CHOICES,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"Feedback - {self.session.title}"
