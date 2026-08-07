from django.db import models

class Course(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    name = models.CharField(max_length=150)

    teacher = models.CharField(
        max_length=150,
        blank=True
    )

    units = models.PositiveIntegerField(default=1)

    difficulty = models.PositiveIntegerField(
        default=5
    )

    exam_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )