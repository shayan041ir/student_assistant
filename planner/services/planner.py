from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from ..models import StudySession, Availability

from .analysis import FeedbackAnalyzer
from .scoring import rank_courses
from .utils import (
    get_weekday_for_availability,
    split_time_range,
)


class StudyPlanner:

    SESSION_DURATION = 60

    def __init__(self, user):

        self.user = user

        self.feedback_analyzer = FeedbackAnalyzer(user)

    def get_courses(self):

        return self.user.courses.all()

    def get_availabilities(self):

        return Availability.objects.filter(user=self.user, is_active=True).order_by(
            "weekday", "start_time"
        )

    def get_feedback_scores(self):

        return self.feedback_analyzer.get_course_need_scores()

    def get_ranked_courses(self):

        courses = self.get_courses()

        feedback_scores = self.get_feedback_scores()

        return rank_courses(courses, feedback_scores)

    def get_week_dates(self, start_date=None):

        if start_date is None:
            start_date = timezone.localdate()

        return [start_date + timedelta(days=i) for i in range(7)]

    def get_available_slots(self, start_date=None):

        dates = self.get_week_dates(start_date)

        availabilities = list(self.get_availabilities())

        slots = []

        for date in dates:

            weekday = get_weekday_for_availability(date)

            day_availabilities = [
                availability
                for availability in availabilities
                if availability.weekday == weekday
            ]

            for availability in day_availabilities:

                time_slots = split_time_range(
                    availability.start_time,
                    availability.end_time,
                    self.SESSION_DURATION,
                )

                for start_time, end_time in time_slots:

                    slots.append(
                        {
                            "date": date,
                            "start_time": start_time,
                            "end_time": end_time,
                        }
                    )

        return slots

    def is_slot_available(self, date, start_time, end_time):

        return not (
            StudySession.objects.filter(
                user=self.user,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exists()
        )

    def calculate_slot_score(self, slot):

        hour = slot["start_time"].hour

        weekday = slot["date"].weekday()

        hour_score = self.feedback_analyzer.get_hour_score(hour)

        weekday_score = self.feedback_analyzer.get_weekday_score(weekday)

        return hour_score * 0.65 + weekday_score * 0.35

    def sort_slots(self, slots):

        return sorted(slots, key=self.calculate_slot_score, reverse=True)

    def choose_course(self, ranked_courses, index):

        if not ranked_courses:
            return None

        return ranked_courses[index % len(ranked_courses)]["course"]

    @transaction.atomic
    def generate_weekly_plan(self, start_date=None):

        if start_date is None:

            start_date = timezone.localdate()

        ranked_courses = self.get_ranked_courses()

        if not ranked_courses:
            return []

        available_slots = self.get_available_slots(start_date)

        available_slots = self.sort_slots(available_slots)

        created_sessions = []

        course_index = 0

        for slot in available_slots:

            date = slot["date"]

            start_time = slot["start_time"]

            end_time = slot["end_time"]

            if not self.is_slot_available(date, start_time, end_time):
                continue

            course = self.choose_course(ranked_courses, course_index)

            if course is None:
                break

            session = StudySession.objects.create(
                user=self.user,
                course=course,
                title=f"مطالعه {course.name}",
                description=("جلسه مطالعه ایجاد شده " "توسط برنامه‌ریز هوشمند."),
                date=date,
                start_time=start_time,
                end_time=end_time,
                status="planned",
            )

            created_sessions.append(session)

            course_index += 1

        return created_sessions
