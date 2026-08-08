from collections import defaultdict

from django.db.models import Avg

from ..models import StudyFeedback


class FeedbackAnalyzer:

    def __init__(self, user):
        self.user = user

    def get_feedbacks(self):
        return (
            StudyFeedback.objects
            .filter(session__user=self.user)
            .select_related(
                "session",
                "session__course",
            )
        )

    def get_average_readiness(self):
        result = self.get_feedbacks().aggregate(
            average=Avg("mental_readiness")
        )

        return round(result["average"] or 0, 2)

    def get_average_focus(self):
        result = self.get_feedbacks().aggregate(
            average=Avg("focus_level")
        )

        return round(result["average"] or 0, 2)

    def get_average_satisfaction(self):
        result = self.get_feedbacks().aggregate(
            average=Avg("satisfaction")
        )

        return round(result["average"] or 0, 2)

    def get_average_difficulty(self):
        result = self.get_feedbacks().aggregate(
            average=Avg("difficulty")
        )

        return round(result["average"] or 0, 2)

    def get_hourly_readiness(self):

        data = defaultdict(list)

        for feedback in self.get_feedbacks():

            hour = feedback.session.start_time.hour

            data[hour].append(
                feedback.mental_readiness
            )

        result = {}

        for hour, values in data.items():

            result[hour] = round(
                sum(values) / len(values),
                2
            )

        return dict(sorted(result.items()))

    def get_weekday_readiness(self):

        data = defaultdict(list)

        for feedback in self.get_feedbacks():

            weekday = feedback.session.date.weekday()

            data[weekday].append(
                feedback.mental_readiness
            )

        result = {}

        for weekday, values in data.items():

            result[weekday] = round(
                sum(values) / len(values),
                2
            )

        return dict(sorted(result.items()))

    def get_best_study_hours(self):

        hourly = self.get_hourly_readiness()

        if not hourly:
            return []

        return sorted(
            hourly,
            key=hourly.get,
            reverse=True
        )

    def get_best_weekdays(self):

        weekday_data = self.get_weekday_readiness()

        if not weekday_data:
            return []

        return sorted(
            weekday_data,
            key=weekday_data.get,
            reverse=True
        )

    def get_course_analysis(self):

        data = defaultdict(list)

        for feedback in self.get_feedbacks():

            course_id = feedback.session.course_id

            score = (
                feedback.mental_readiness
                + feedback.focus_level
                + feedback.satisfaction
            ) / 3

            data[course_id].append(score)

        result = {}

        for course_id, values in data.items():

            result[course_id] = round(
                sum(values) / len(values),
                2
            )

        return result

    def get_course_need_scores(self):

        analysis = self.get_course_analysis()

        result = {}

        for course_id, average in analysis.items():

            need_score = 6 - average

            result[course_id] = round(
                max(
                    1,
                    min(
                        10,
                        need_score * 2
                    )
                ),
                2
            )

        return result

    def get_hour_score(self, hour):

        hourly = self.get_hourly_readiness()

        if not hourly:
            return 5

        if hour not in hourly:
            return 5

        return hourly[hour]

    def get_weekday_score(self, weekday):

        weekday_data = self.get_weekday_readiness()

        if not weekday_data:
            return 5

        if weekday not in weekday_data:
            return 5

        return weekday_data[weekday]

    def get_summary(self):

        return {
            "average_readiness": self.get_average_readiness(),
            "average_focus": self.get_average_focus(),
            "average_satisfaction": self.get_average_satisfaction(),
            "average_difficulty": self.get_average_difficulty(),
            "best_hours": self.get_best_study_hours(),
            "best_weekdays": self.get_best_weekdays(),
            "hourly_readiness": self.get_hourly_readiness(),
            "weekday_readiness": self.get_weekday_readiness(),
            "course_analysis": self.get_course_analysis(),
            "course_need_scores": self.get_course_need_scores(),
        }