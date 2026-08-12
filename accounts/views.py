from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from django.utils import timezone

from courses.models import Course
from notes.models import Note
from tasks.models import Task
from planner.models import StudySession


def register(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if not username or not password:
            messages.error(
                request,
                "نام کاربری و رمز عبور الزامی است.",
            )

            return redirect("accounts:register")

        if password != password2:
            messages.error(
                request,
                "رمزهای عبور یکسان نیستند.",
            )

            return redirect("accounts:register")

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "این نام کاربری قبلاً ثبت شده است.",
            )

            return redirect("accounts:register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        login(request, user)

        messages.success(
            request,
            "ثبت‌نام با موفقیت انجام شد.",
        )

        return redirect("/")

    return render(
        request,
        "accounts/register.html",
    )


@login_required
def dashboard(request):
    user = request.user
    today = timezone.localdate()

    # -------------------------
    # آمار کلی
    # -------------------------

    courses_count = Course.objects.filter(user=user).count()

    notes_count = Note.objects.filter(user=user).count()

    tasks_count = Task.objects.filter(user=user).count()

    # -------------------------
    # تکالیف در انتظار
    # -------------------------

    pending_tasks = (
        Task.objects.filter(
            user=user,
            status="pending",
        )
        .select_related("course")
        .order_by("due_date")[:5]
    )

    # -------------------------
    # جلسات مطالعه امروز
    # -------------------------

    today_sessions = (
        StudySession.objects.filter(
            user=user,
            date=today,
        )
        .select_related("course")
        .order_by("start_time")
    )

    # -------------------------
    # تعداد جلسات امروز
    # -------------------------

    today_sessions_count = today_sessions.count()

    today_completed_sessions = today_sessions.filter(status="completed").count()

    today_pending_sessions = today_sessions.filter(status="planned").count()

    # -------------------------
    # جلسات آینده
    # -------------------------

    upcoming_sessions = (
        StudySession.objects.filter(
            user=user,
            date__gte=today,
            status="planned",
        )
        .select_related("course")
        .order_by(
            "date",
            "start_time",
        )[:5]
    )

    # -------------------------
    # جلسات انجام شده
    # -------------------------

    completed_sessions_count = StudySession.objects.filter(
        user=user,
        status="completed",
    ).count()

    # -------------------------
    # جلسات برنامه‌ریزی شده
    # -------------------------

    planned_sessions_count = StudySession.objects.filter(
        user=user,
        status="planned",
    ).count()

    # -------------------------
    # وضعیت مطالعه امروز
    # -------------------------

    if today_sessions_count > 0:
        study_progress = int((today_completed_sessions / today_sessions_count) * 100)
    else:
        study_progress = 0

    context = {
        "courses_count": courses_count,
        "notes_count": notes_count,
        "tasks_count": tasks_count,
        "pending_tasks": pending_tasks,
        "today": today,
        "today_sessions": today_sessions,
        "today_sessions_count": today_sessions_count,
        "today_completed_sessions": today_completed_sessions,
        "today_pending_sessions": today_pending_sessions,
        "upcoming_sessions": upcoming_sessions,
        "completed_sessions_count": completed_sessions_count,
        "planned_sessions_count": planned_sessions_count,
        "study_progress": study_progress,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )
