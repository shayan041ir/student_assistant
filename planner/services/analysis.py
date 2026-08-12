def get_course_feedbacks(course):
    """
    دریافت Feedbackهای یک درس.
    """

    sessions = course.study_sessions.filter(feedback__isnull=False).select_related(
        "feedback"
    )

    return [session.feedback for session in sessions]


def get_user_feedbacks(user):
    """
    دریافت تمام Feedbackهای کاربر.
    """

    sessions = user.study_sessions.filter(feedback__isnull=False).select_related(
        "feedback"
    )

    return [session.feedback for session in sessions]


def calculate_feedback_average(
    feedbacks,
    attribute,
):
    """
    محاسبه میانگین یک ویژگی Feedback.
    """

    if not feedbacks:
        return 0

    values = [getattr(feedback, attribute) for feedback in feedbacks]

    if not values:
        return 0

    return round(
        sum(values) / len(values),
        2,
    )


def get_course_feedback_analysis(course):
    """
    تحلیل Feedbackهای یک درس.
    """

    feedbacks = get_course_feedbacks(course)

    if not feedbacks:
        return {
            "count": 0,
            "average_readiness": 0,
            "average_satisfaction": 0,
            "average_focus": 0,
            "average_difficulty": 0,
        }

    return {
        "count": len(feedbacks),
        "average_readiness": calculate_feedback_average(
            feedbacks,
            "mental_readiness",
        ),
        "average_satisfaction": calculate_feedback_average(
            feedbacks,
            "satisfaction",
        ),
        "average_focus": calculate_feedback_average(
            feedbacks,
            "focus_level",
        ),
        "average_difficulty": calculate_feedback_average(
            feedbacks,
            "difficulty",
        ),
    }


def get_user_feedback_analysis(user):
    """
    تحلیل کلی عملکرد کاربر.
    """

    feedbacks = get_user_feedbacks(user)

    if not feedbacks:
        return {
            "count": 0,
            "average_readiness": 0,
            "average_satisfaction": 0,
            "average_focus": 0,
            "average_difficulty": 0,
        }

    return {
        "count": len(feedbacks),
        "average_readiness": calculate_feedback_average(
            feedbacks,
            "mental_readiness",
        ),
        "average_satisfaction": calculate_feedback_average(
            feedbacks,
            "satisfaction",
        ),
        "average_focus": calculate_feedback_average(
            feedbacks,
            "focus_level",
        ),
        "average_difficulty": calculate_feedback_average(
            feedbacks,
            "difficulty",
        ),
    }


def get_best_study_hours(user):
    """
    پیدا کردن ساعت‌هایی که کاربر
    در آن‌ها Focus بهتری داشته است.
    """

    sessions = user.study_sessions.filter(feedback__isnull=False).select_related(
        "feedback"
    )

    hour_scores = {}

    for session in sessions:

        hour = session.start_time.hour

        focus = session.feedback.focus_level

        hour_scores.setdefault(
            hour,
            [],
        ).append(focus)

    results = []

    for hour, scores in hour_scores.items():

        if not scores:
            continue

        average = sum(scores) / len(scores)

        results.append(
            {
                "hour": hour,
                "average_focus": round(
                    average,
                    2,
                ),
                "sessions": len(scores),
            }
        )

    results.sort(
        key=lambda item: item["average_focus"],
        reverse=True,
    )

    return results


def get_best_weekdays(user):
    """
    پیدا کردن روزهایی که کاربر
    Focus بهتری داشته است.

    خروجی weekday بر اساس سیستم Python است:

        0 = Monday
        ...
        6 = Sunday
    """

    sessions = user.study_sessions.filter(feedback__isnull=False).select_related(
        "feedback"
    )

    weekday_scores = {}

    for session in sessions:

        weekday = session.date.weekday()

        focus = session.feedback.focus_level

        weekday_scores.setdefault(
            weekday,
            [],
        ).append(focus)

    results = []

    for weekday, scores in weekday_scores.items():

        if not scores:
            continue

        average = sum(scores) / len(scores)

        results.append(
            {
                "weekday": weekday,
                "average_focus": round(
                    average,
                    2,
                ),
                "sessions": len(scores),
            }
        )

    results.sort(
        key=lambda item: item["average_focus"],
        reverse=True,
    )

    return results
