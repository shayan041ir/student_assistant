from datetime import time


def time_to_minutes(value):
    """
    تبدیل time به تعداد دقیقه از ابتدای روز.

    08:30 -> 510
    """

    return value.hour * 60 + value.minute


def minutes_to_time(minutes):
    """
    تبدیل تعداد دقیقه به time.

    510 -> 08:30
    """

    minutes = minutes % (24 * 60)

    hour = minutes // 60
    minute = minutes % 60

    return time(
        hour=hour,
        minute=minute,
    )


def calculate_duration(start_time, end_time):
    """
    محاسبه مدت زمان بین دو ساعت.
    """

    start = time_to_minutes(start_time)
    end = time_to_minutes(end_time)

    if end <= start:
        return 0

    return end - start


def split_time_range(
    start_time,
    end_time,
    session_minutes=60,
):
    """
    تقسیم یک بازه زمانی به Sessionهای مساوی.

    مثال:

    14:00 -> 17:00

    خروجی:

    14:00 -> 15:00
    15:00 -> 16:00
    16:00 -> 17:00
    """

    if session_minutes <= 0:
        return []

    start = time_to_minutes(start_time)
    end = time_to_minutes(end_time)

    if end <= start:
        return []

    sessions = []

    current = start

    while current + session_minutes <= end:

        session_start = minutes_to_time(current)

        session_end = minutes_to_time(current + session_minutes)

        sessions.append(
            (
                session_start,
                session_end,
            )
        )

        current += session_minutes

    return sessions


def python_weekday_to_persian_weekday(
    python_weekday,
):
    """
    تبدیل weekday پایتون به weekday پروژه.

    Python:

    0 Monday
    1 Tuesday
    2 Wednesday
    3 Thursday
    4 Friday
    5 Saturday
    6 Sunday

    Project:

    0 Saturday
    1 Sunday
    2 Monday
    3 Tuesday
    4 Wednesday
    5 Thursday
    6 Friday
    """

    return (python_weekday + 2) % 7


def persian_weekday_to_python_weekday(
    project_weekday,
):
    """
    تبدیل weekday پروژه به weekday پایتون.
    """

    return (project_weekday + 5) % 7
