from django.utils import timezone

from tasks.models import Task

from .utils import calculate_days_until


def exam_urgency_score(course):

    if not course.exam_date:
        return 0

    today = timezone.localdate()

    days_left = calculate_days_until(course.exam_date, today)

    if days_left < 0:
        return 0

    if days_left == 0:
        return 10

    if days_left <= 3:
        return 9

    if days_left <= 7:
        return 8

    if days_left <= 14:
        return 6

    if days_left <= 30:
        return 4

    return 2


def difficulty_score(course):

    difficulty = course.difficulty or 5

    return min(10, max(0, difficulty))


def task_urgency_score(course):

    today = timezone.localdate()

    tasks = Task.objects.filter(user=course.user, course=course, status="pending")

    if not tasks.exists():
        return 0

    highest_score = 0

    for task in tasks:

        if not task.due_date:

            score = 2

        else:

            days_left = (task.due_date - today).days

            if days_left <= 0:
                score = 10

            elif days_left <= 2:
                score = 9

            elif days_left <= 7:
                score = 7

            elif days_left <= 14:
                score = 4

            else:
                score = 2

        highest_score = max(highest_score, score)

    return highest_score


def calculate_course_priority(course, feedback_score=5):

    exam_score = exam_urgency_score(course)

    difficulty = difficulty_score(course)

    task_score = task_urgency_score(course)

    final_score = (
        exam_score * 0.40
        + difficulty * 0.25
        + task_score * 0.20
        + feedback_score * 0.15
    )

    return round(final_score, 2)


def rank_courses(courses, feedback_scores=None):

    if feedback_scores is None:
        feedback_scores = {}

    ranked = []

    for course in courses:

        feedback_score = feedback_scores.get(course.id, 5)

        score = calculate_course_priority(course, feedback_score)

        ranked.append(
            {
                "course": course,
                "score": score,
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)

    return ranked
