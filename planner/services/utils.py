from datetime import datetime, timedelta


def get_weekday_for_availability(date):
    """
    تبدیل weekday استاندارد پایتون به weekday مورد استفاده
    در مدل Availability.

    Python:
        Monday = 0
        Tuesday = 1
        ...
        Sunday = 6

    سیستم ما:
        Saturday = 0
        Sunday = 1
        ...
        Friday = 6
    """

    return (date.weekday() + 2) % 7


def combine_date_time(date, time):
    """
    ترکیب تاریخ و ساعت و ساخت datetime
    """

    return datetime.combine(date, time)


def get_duration_minutes(start_time, end_time):
    """
    محاسبه مدت زمان بین دو ساعت بر حسب دقیقه.
    """

    start = datetime.combine(datetime.today(), start_time)

    end = datetime.combine(datetime.today(), end_time)

    if end <= start:
        return 0

    return int((end - start).total_seconds() / 60)


def split_time_range(start_time, end_time, duration_minutes=60):
    """
    یک بازه زمانی را به چند Session تقسیم می‌کند.

    مثال:

    08:00 - 11:00

    با duration=60:

    08:00 - 09:00
    09:00 - 10:00
    10:00 - 11:00
    """

    current = datetime.combine(datetime.today(), start_time)

    end = datetime.combine(datetime.today(), end_time)

    slots = []

    while current + timedelta(minutes=duration_minutes) <= end:

        slot_start = current.time()

        slot_end = (current + timedelta(minutes=duration_minutes)).time()

        slots.append((slot_start, slot_end))

        current += timedelta(minutes=duration_minutes)

    return slots


def calculate_days_until(date, today=None):
    """
    تعداد روز باقی‌مانده تا یک تاریخ.
    """

    if today is None:
        today = datetime.today().date()

    return (date - today).days


def is_time_range_overlapping(start1, end1, start2, end2):
    """
    بررسی overlap شدن دو بازه زمانی.
    """

    return start1 < end2 and start2 < end1
