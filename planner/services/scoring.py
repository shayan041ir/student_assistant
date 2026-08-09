from django.utils import timezone


def calculate_exam_score(course):
    """
    محاسبه امتیاز بر اساس نزدیک بودن امتحان.
    """

    if not course.exam_date:
        return 0

    today = timezone.localdate()

    days_remaining = (course.exam_date - today).days

    if days_remaining < 0:
        return 0

    if days_remaining == 0:
        return 50

    if days_remaining <= 3:
        return 40

    if days_remaining <= 7:
        return 30

    if days_remaining <= 14:
        return 20

    if days_remaining <= 30:
        return 10

    return 5


def calculate_difficulty_score(course):
    """
    محاسبه امتیاز سختی درس.
    """

    difficulty = course.difficulty or 1

    return min(difficulty * 3, 30)


def calculate_task_score(course):
    """
    محاسبه امتیاز بر اساس تعداد تکالیف باز.
    """

    pending_tasks = course.tasks.filter(status="pending").count()

    return min(pending_tasks * 5, 25)


def calculate_feedback_score(course):
    """
    تحلیل Feedbackهای قبلی درس.

    تمرکز پایین:
        نیاز بیشتر به مطالعه

    آمادگی پایین:
        نیاز بیشتر به مطالعه

    سختی بالا:
        نیاز بیشتر به مطالعه
    """

    feedbacks = []

    sessions = course.study_sessions.filter(feedback__isnull=False).select_related(
        "feedback"
    )

    for session in sessions:
        feedbacks.append(session.feedback)

    if not feedbacks:
        return 0

    total = 0

    for feedback in feedbacks:

        if feedback.mental_readiness <= 2:
            total += 5

        if feedback.focus_level <= 2:
            total += 5

        if feedback.difficulty >= 4:
            total += 5

    return min(total, 25)


def calculate_course_score(course):
    """
    محاسبه امتیاز نهایی یک درس.
    """

    exam_score = calculate_exam_score(course)

    difficulty_score = calculate_difficulty_score(course)

    task_score = calculate_task_score(course)

    feedback_score = calculate_feedback_score(course)

    total_score = exam_score + difficulty_score + task_score + feedback_score

    return {
        "course": course,
        "exam_score": exam_score,
        "difficulty_score": difficulty_score,
        "task_score": task_score,
        "feedback_score": feedback_score,
        "total_score": total_score,
    }


def rank_courses(courses):
    """
    تمام درس‌ها را امتیازدهی و از بیشترین
    اولویت به کمترین مرتب می‌کند.
    """

    results = [calculate_course_score(course) for course in courses]

    results.sort(
        key=lambda item: item["total_score"],
        reverse=True,
    )

    return results
