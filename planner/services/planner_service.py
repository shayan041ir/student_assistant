from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from planner.models import StudySession
from planner.services.analysis import get_best_study_hours
from planner.services.scoring import rank_courses
from planner.utils.time_utils import (
    calculate_duration,
    get_project_weekday,
    split_time_range,
)

DEFAULT_SESSION_MINUTES = 60


def get_available_slots(user):
    """
    دریافت زمان‌های آزاد فعال کاربر.
    """

    return user.availabilities.filter(is_active=True).order_by(
        "weekday",
        "start_time",
    )


def get_courses_for_planning(user):
    """
    دریافت و رتبه‌بندی درس‌های کاربر.
    """

    courses = user.courses.all().prefetch_related(
        "tasks",
        "study_sessions",
    )

    return rank_courses(courses)


def session_already_exists(
    user,
    date,
    start_time,
    end_time,
):
    """
    بررسی وجود دقیق یک جلسه مشابه.
    """

    return StudySession.objects.filter(
        user=user,
        date=date,
        start_time=start_time,
        end_time=end_time,
    ).exists()


def has_time_conflict(
    user,
    date,
    start_time,
    end_time,
):
    """
    بررسی هر نوع تداخل زمانی.
    """

    return StudySession.objects.filter(
        user=user,
        date=date,
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).exists()


def get_next_course(
    ranked_courses,
    course_index,
):
    """
    انتخاب درس بعدی از لیست رتبه‌بندی‌شده.
    """

    if not ranked_courses:
        return None

    return ranked_courses[course_index % len(ranked_courses)]


def get_preferred_hours(user):
    """
    دریافت ساعت‌هایی که کاربر در آن‌ها
    Focus بهتری داشته است.

    خروجی:
        set[int]
    """

    best_hours = get_best_study_hours(user)

    return {item["hour"] for item in best_hours if item["average_focus"] >= 3.5}


def sort_time_ranges_by_preference(
    time_ranges,
    preferred_hours,
):
    """
    قرار دادن بازه‌های دارای Focus بهتر
    در ابتدای لیست.
    """

    return sorted(
        time_ranges,
        key=lambda item: (
            item[0].hour not in preferred_hours,
            item[0],
        ),
    )


def get_session_date(
    start_date,
    project_weekday,
):
    """
    تبدیل weekday پروژه به تاریخ واقعی.

    سیستم پروژه:

        0 = شنبه
        1 = یکشنبه
        2 = دوشنبه
        3 = سه‌شنبه
        4 = چهارشنبه
        5 = پنجشنبه
        6 = جمعه
    """

    current_project_weekday = get_project_weekday(start_date)

    days_until = (project_weekday - current_project_weekday) % 7

    return start_date + timedelta(days=days_until)


def generate_weekly_plan(
    user,
    start_date=None,
    session_minutes=DEFAULT_SESSION_MINUTES,
):
    """
    ساخت برنامه مطالعه هفتگی.

    قوانین:

    1. فقط Availability فعال استفاده می‌شود.
    2. فقط درس‌های همان کاربر استفاده می‌شوند.
    3. درس‌ها بر اساس Score رتبه‌بندی می‌شوند.
    4. ساعت‌های دارای Focus بهتر در اولویت هستند.
    5. جلسه تکراری ایجاد نمی‌شود.
    6. جلسه متداخل ایجاد نمی‌شود.
    7. هر جلسه طول مشخصی دارد.
    """

    if start_date is None:
        start_date = timezone.localdate()

    if session_minutes <= 0:
        raise ValueError("مدت جلسه باید بیشتر از صفر باشد.")

    available_slots = list(get_available_slots(user))

    ranked_courses = get_courses_for_planning(user)

    if not available_slots:
        return []

    if not ranked_courses:
        return []

    preferred_hours = get_preferred_hours(user)

    created_sessions = []

    course_index = 0

    with transaction.atomic():

        for availability in available_slots:

            if availability.start_time >= availability.end_time:
                continue

            duration = calculate_duration(
                availability.start_time,
                availability.end_time,
            )

            if duration < session_minutes:
                continue

            session_date = get_session_date(
                start_date=start_date,
                project_weekday=availability.weekday,
            )

            time_ranges = split_time_range(
                availability.start_time,
                availability.end_time,
                session_minutes=session_minutes,
            )

            time_ranges = sort_time_ranges_by_preference(
                time_ranges,
                preferred_hours,
            )

            for start_time, end_time in time_ranges:

                if session_already_exists(
                    user=user,
                    date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                ):
                    continue

                if has_time_conflict(
                    user=user,
                    date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                ):
                    continue

                selected_course = get_next_course(
                    ranked_courses,
                    course_index,
                )

                if not selected_course:
                    continue

                course = selected_course["course"]

                session = StudySession.objects.create(
                    user=user,
                    course=course,
                    title=f"مطالعه {course.name}",
                    description=(
                        "این جلسه توسط برنامه‌ریز هوشمند "
                        "بر اساس اولویت درس، زمان آزاد "
                        "و عملکرد قبلی ایجاد شده است."
                    ),
                    date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                    status="planned",
                )

                created_sessions.append(session)

                course_index += 1

    return created_sessions
