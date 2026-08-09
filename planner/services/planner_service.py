from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from planner.models import StudySession
from planner.services.scoring import rank_courses
from planner.utils.time_utils import split_time_range

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


def session_exists(
    user,
    date,
    start_time,
    end_time,
):
    """
    بررسی می‌کند آیا در این بازه قبلاً جلسه‌ای وجود دارد یا خیر.
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
        status__in=["planned", "completed"],
    ).exists()


def get_week_start(start_date=None):
    """
    مشخص می‌کند برنامه از چه تاریخی شروع شود.

    اگر تاریخ داده نشود، امروز استفاده می‌شود.
    """

    if start_date is None:
        start_date = timezone.localdate()

    return start_date


def generate_weekly_plan(
    user,
    start_date=None,
    session_minutes=DEFAULT_SESSION_MINUTES,
):
    """
    تولید برنامه مطالعه برای یک هفته.

    قوانین:
    - فقط زمان‌های آزاد فعال استفاده می‌شوند.
    - فقط درس‌های متعلق به کاربر استفاده می‌شوند.
    - درس‌ها بر اساس Score مرتب می‌شوند.
    - Sessionهای تکراری ایجاد نمی‌شوند.
    - Sessionهای دارای تداخل زمانی ایجاد نمی‌شوند.
    """

    start_date = get_week_start(start_date)

    available_slots = list(get_available_slots(user))
    ranked_courses = get_courses_for_planning(user)

    if not available_slots:
        return []

    if not ranked_courses:
        return []

    created_sessions = []

    course_index = 0

    with transaction.atomic():

        for availability in available_slots:

            weekday = availability.weekday

            # تبدیل weekday پروژه به تاریخ واقعی
            days_until = (weekday - ((start_date.weekday() + 2) % 7)) % 7

            session_date = start_date + timedelta(days=days_until)

            time_ranges = split_time_range(
                availability.start_time,
                availability.end_time,
                session_minutes=session_minutes,
            )

            for start_time, end_time in time_ranges:

                # اگر زمان جلسه قبل از امروز باشد،
                # آن را ایجاد نکن.
                if session_date < start_date:
                    continue

                # جلوگیری از ایجاد Session تکراری
                if session_exists(
                    user=user,
                    date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                ):
                    continue

                # جلوگیری از تداخل زمانی
                if has_time_conflict(
                    user=user,
                    date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                ):
                    continue

                selected_course = ranked_courses[course_index % len(ranked_courses)]

                course = selected_course["course"]

                title = f"مطالعه {course.name}"

                session = StudySession.objects.create(
                    user=user,
                    course=course,
                    title=title,
                    description=(
                        "این جلسه توسط برنامه‌ریز هوشمند "
                        "بر اساس زمان آزاد و اولویت درس ایجاد شده است."
                    ),
                    date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                    status="planned",
                )

                created_sessions.append(session)

                course_index += 1

    return created_sessions
