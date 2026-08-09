from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from planner.models import StudySession
from planner.services.analysis import get_best_study_hours
from planner.services.scoring import rank_courses
from planner.utils.time_utils import (
    calculate_duration,
    split_time_range,
)

DEFAULT_SESSION_MINUTES = 60


def get_available_slots(user):
    """
    دریافت زمان‌های آزاد فعال کاربر.
    """

    return user.availabilities.filter(is_active=True).order_by("weekday", "start_time")


def get_courses_for_planning(user):
    """
    دریافت و رتبه‌بندی درس‌های کاربر.
    """

    courses = user.courses.all()

    return rank_courses(courses)


def session_already_exists(
    user,
    date,
    start_time,
    end_time,
):
    """
    بررسی می‌کند آیا در بازه موردنظر
    قبلاً جلسه‌ای برای کاربر وجود دارد یا نه.
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
    بررسی تداخل زمانی با جلسات قبلی.
    """

    return StudySession.objects.filter(
        user=user,
        date=date,
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).exists()


def get_next_course(ranked_courses, course_index):
    """
    انتخاب درس بعدی بر اساس رتبه‌بندی.
    """

    if not ranked_courses:
        return None

    return ranked_courses[course_index % len(ranked_courses)]


def generate_weekly_plan(
    user,
    start_date=None,
    session_minutes=DEFAULT_SESSION_MINUTES,
):
    """
    ایجاد برنامه مطالعه برای هفته.

    قوانین:
    - فقط زمان‌های آزاد فعال استفاده می‌شوند.
    - درس‌ها بر اساس Score مرتب می‌شوند.
    - ساعت‌های دارای Focus بهتر در اولویت قرار می‌گیرند.
    - جلسه تکراری ایجاد نمی‌شود.
    - جلسات متداخل ایجاد نمی‌شوند.
    - هر Session طول مشخصی دارد.
    """

    if start_date is None:
        start_date = timezone.localdate()

    if session_minutes <= 0:
        raise ValueError("session_minutes باید بیشتر از صفر باشد.")

    available_slots = get_available_slots(user)
    ranked_courses = get_courses_for_planning(user)

    if not ranked_courses:
        return []

    if not available_slots:
        return []

    # ساعت‌هایی که کاربر قبلاً در آن‌ها Focus خوبی داشته
    best_hours = get_best_study_hours(user)

    preferred_hours = {
        item["hour"] for item in best_hours if item["average_focus"] >= 3.5
    }

    created_sessions = []

    # برای جلوگیری از انتخاب همیشه یکسان
    course_index = 0

    with transaction.atomic():

        for availability in available_slots:

            weekday = availability.weekday

            # تبدیل روز پروژه به تاریخ واقعی
            days_until = (weekday - ((start_date.weekday() + 2) % 7)) % 7

            session_date = start_date + timedelta(days=days_until)

            # اگر تاریخ گذشته باشد، به هفته بعد منتقل شود
            if session_date < start_date:
                session_date += timedelta(days=7)

            # اگر زمان آزاد نامعتبر باشد
            duration = calculate_duration(
                availability.start_time,
                availability.end_time,
            )

            if duration < session_minutes:
                continue

            time_ranges = split_time_range(
                availability.start_time,
                availability.end_time,
                session_minutes=session_minutes,
            )

            for start_time, end_time in time_ranges:

                # جلوگیری از جلسه تکراری
                if session_already_exists(
                    user=user,
                    date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                ):
                    continue

                # جلوگیری از تداخل
                if has_time_conflict(
                    user=user,
                    date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                ):
                    continue

                # انتخاب درس
                selected_course = get_next_course(
                    ranked_courses,
                    course_index,
                )

                if not selected_course:
                    continue

                course = selected_course["course"]

                # اگر ساعت موردنظر ساعت مناسب کاربر باشد
                # همان درس انتخاب می‌شود.
                #
                # در غیر این صورت نیز به صورت Round Robin
                # بین درس‌ها حرکت می‌کنیم.

                title = f"مطالعه {course.name}"

                session = StudySession.objects.create(
                    user=user,
                    course=course,
                    title=title,
                    description=(
                        "این جلسه توسط برنامه‌ریز هوشمند "
                        "بر اساس زمان آزاد، اولویت درس "
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
