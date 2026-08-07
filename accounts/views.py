from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from courses.models import Course
from notes.models import Note
from tasks.models import Task


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
                "نام کاربری و رمز عبور الزامی است."
            )

            return redirect("accounts:register")

        if password != password2:

            messages.error(
                request,
                "رمزهای عبور یکسان نیستند."
            )

            return redirect("accounts:register")

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "این نام کاربری قبلاً ثبت شده است."
            )

            return redirect("accounts:register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        messages.success(
            request,
            "ثبت‌نام با موفقیت انجام شد."
        )

        return redirect("/")

    return render(
        request,
        "accounts/register.html"
    )




@login_required
def dashboard(request):

    courses_count = Course.objects.filter(
        user=request.user
    ).count()

    notes_count = Note.objects.filter(
        user=request.user
    ).count()

    tasks_count = Task.objects.filter(
        user=request.user
    ).count()

    pending_tasks = Task.objects.filter(
        user=request.user,
        status="pending"
    ).order_by("due_date")[:5]

    context = {
        "courses_count": courses_count,
        "notes_count": notes_count,
        "tasks_count": tasks_count,
        "pending_tasks": pending_tasks,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )