from django.utils import timezone


def calculate_exam_score(course):
    """
    امتیاز نزدیکی امتحان.

    امتحان نزدیک‌تر = اولویت بیشتر.
    """

    if not course.exam_date:
        return 0

    today = timezone.localdate()

    days_remaining = (
        course.exam_date - today
    ).days

    if days_remaining < 0:
        return 0

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
    امتیاز سختی درس.

    difficulty بین 1 تا 10 است.
    """

    difficulty = course.difficulty or 1

    difficulty = max(
        1,
        min(difficulty, 10),
    )

    return difficulty * 3


def calculate_task_score(course):
    """
    امتیاز تعداد تکالیف در انتظار.

    هر تکلیف:
        +5

    حداکثر:
        25
    """

    pending_tasks = (
        course.tasks
        .filter(status="pending")
        .count()
    )

    return min(
        pending_tasks * 5,
        25,
    )


def calculate_feedback_score(course):
    """
    امتیاز Feedbackهای قبلی.

    Focus پایین:
        +5

    آمادگی ذهنی پایین:
        +5

    سختی بالا:
        +5

    حداکثر:
        25
    """

    sessions = (
        course.study_sessions
        .filter(feedback__isnull=False)
        .select_related("feedback")
    )

    total = 0

    for session in sessions:

        feedback = session.feedback

        if feedback.mental_readiness <= 2:
            total += 5

        if feedback.focus_level <= 2:
            total += 5

        if feedback.difficulty >= 4:
            total += 5

    return min(
        total,
        25,
    )


def calculate_course_score(course):
    """
    محاسبه امتیاز نهایی درس.
    """

    exam_score = calculate_exam_score(
        course
    )

    difficulty_score = calculate_difficulty_score(
        course
    )

    task_score = calculate_task_score(
        course
    )

    feedback_score = calculate_feedback_score(
        course
    )

    total_score = (
        exam_score
        + difficulty_score
        + task_score
        + feedback_score
    )

    return {
        "course": course,
        "exam_score": exam_score,
        "difficulty_score": difficulty_score,
        "task_score": task_score,
        "feedback_score": feedback_score,
        "total_score": total_score,
    }


def calculate_course_priority(course):
    """
    نام جایگزین برای دریافت اولویت درس.
    """

    return calculate_course_score(
        course
    )


def rank_courses(courses):
    """
    امتیازدهی و مرتب‌سازی درس‌ها
    از بیشترین اولویت به کمترین.
    """

    results = [
        calculate_course_score(course)
        for course in courses
    ]

    results.sort(
        key=lambda item: item["total_score"],
        reverse=True,
    )

    return results