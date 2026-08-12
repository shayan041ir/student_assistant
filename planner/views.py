from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import (
    AvailabilityForm,
    StudyFeedbackForm,
    StudySessionForm,
)
from .models import (
    Availability,
    StudyFeedback,
    StudySession,
)
from .services.planner_service import generate_weekly_plan


def _set_course_queryset(form, user):
    form.fields["course"].queryset = user.courses.all()


def _has_session_conflict(
    user,
    date,
    start_time,
    end_time,
    exclude_pk=None,
):
    queryset = StudySession.objects.filter(
        user=user,
        date=date,
        start_time__lt=end_time,
        end_time__gt=start_time,
    )

    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)

    return queryset.exists()


@login_required
def index(request):
    sessions = (
        StudySession.objects.filter(user=request.user)
        .select_related("course")
        .prefetch_related("feedback")
        .order_by(
            "date",
            "start_time",
        )
    )

    return render(
        request,
        "planner/index.html",
        {
            "sessions": sessions,
        },
    )


@login_required
def create_session(request):

    if request.method == "POST":

        form = StudySessionForm(request.POST)

        _set_course_queryset(
            form,
            request.user,
        )

        if form.is_valid():

            date = form.cleaned_data["date"]
            start_time = form.cleaned_data["start_time"]
            end_time = form.cleaned_data["end_time"]

            if _has_session_conflict(
                user=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time,
            ):
                form.add_error(
                    None,
                    "این بازه زمانی با یک جلسه مطالعه دیگر تداخل دارد.",
                )

            else:

                session = form.save(commit=False)

                session.user = request.user
                session.status = "planned"

                session.save()

                messages.success(
                    request,
                    "جلسه مطالعه با موفقیت ایجاد شد.",
                )

                return redirect("planner:index")

    else:

        form = StudySessionForm()

        _set_course_queryset(
            form,
            request.user,
        )

    return render(
        request,
        "planner/form.html",
        {
            "form": form,
            "title": "افزودن جلسه مطالعه",
        },
    )


@login_required
def update_session(request, pk):

    session = get_object_or_404(
        StudySession,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        form = StudySessionForm(
            request.POST,
            instance=session,
        )

        _set_course_queryset(
            form,
            request.user,
        )

        if form.is_valid():

            date = form.cleaned_data["date"]
            start_time = form.cleaned_data["start_time"]
            end_time = form.cleaned_data["end_time"]

            if _has_session_conflict(
                user=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time,
                exclude_pk=session.pk,
            ):
                form.add_error(
                    None,
                    "این بازه زمانی با یک جلسه مطالعه دیگر تداخل دارد.",
                )

            else:

                updated_session = form.save(commit=False)

                updated_session.status = session.status

                updated_session.save()

                messages.success(
                    request,
                    "جلسه مطالعه با موفقیت ویرایش شد.",
                )

                return redirect("planner:index")

    else:

        form = StudySessionForm(instance=session)

        _set_course_queryset(
            form,
            request.user,
        )

    return render(
        request,
        "planner/form.html",
        {
            "form": form,
            "title": "ویرایش جلسه مطالعه",
        },
    )


@login_required
def delete_session(request, pk):

    session = get_object_or_404(
        StudySession,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        session.delete()

        messages.success(
            request,
            "جلسه مطالعه با موفقیت حذف شد.",
        )

        return redirect("planner:index")

    return render(
        request,
        "planner/delete.html",
        {
            "session": session,
        },
    )


@login_required
def complete_session(request, pk):

    session = get_object_or_404(
        StudySession,
        pk=pk,
        user=request.user,
    )

    if session.status == "completed":

        messages.info(
            request,
            "این جلسه قبلاً انجام‌شده ثبت شده است.",
        )

        return redirect("planner:index")

    session.status = "completed"

    session.save(update_fields=["status"])

    messages.success(
        request,
        "جلسه مطالعه به عنوان انجام‌شده ثبت شد.",
    )

    return redirect("planner:index")


@login_required
def availability_list(request):

    availabilities = Availability.objects.filter(user=request.user).order_by(
        "weekday",
        "start_time",
    )

    return render(
        request,
        "planner/availability_list.html",
        {
            "availabilities": availabilities,
        },
    )


@login_required
def availability_create(request):

    if request.method == "POST":

        form = AvailabilityForm(request.POST)

        if form.is_valid():

            availability = form.save(commit=False)

            availability.user = request.user

            availability.save()

            messages.success(
                request,
                "زمان آزاد با موفقیت اضافه شد.",
            )

            return redirect("planner:availability_list")

    else:

        form = AvailabilityForm()

    return render(
        request,
        "planner/availability_form.html",
        {
            "form": form,
            "title": "افزودن زمان آزاد",
        },
    )


@login_required
def availability_toggle(request, pk):

    availability = get_object_or_404(
        Availability,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        availability.is_active = not availability.is_active

        availability.save(update_fields=["is_active"])

        if availability.is_active:

            messages.success(
                request,
                "زمان آزاد فعال شد.",
            )

        else:

            messages.info(
                request,
                "زمان آزاد غیرفعال شد.",
            )

    return redirect("planner:availability_list")


@login_required
def availability_delete(request, pk):

    availability = get_object_or_404(
        Availability,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        availability.delete()

        messages.success(
            request,
            "زمان آزاد حذف شد.",
        )

    return redirect("planner:availability_list")


@login_required
def create_feedback(request, pk):

    session = get_object_or_404(
        StudySession,
        pk=pk,
        user=request.user,
    )

    if session.status != "completed":

        messages.warning(
            request,
            "ابتدا باید جلسه مطالعه را به عنوان انجام‌شده ثبت کنید.",
        )

        return redirect("planner:index")

    if hasattr(session, "feedback"):

        messages.info(
            request,
            "برای این جلسه قبلاً بازخورد ثبت شده است.",
        )

        return redirect("planner:index")

    if request.method == "POST":

        form = StudyFeedbackForm(request.POST)

        if form.is_valid():

            feedback = form.save(commit=False)

            feedback.session = session

            feedback.save()

            messages.success(
                request,
                "بازخورد جلسه با موفقیت ثبت شد.",
            )

            return redirect("planner:index")

    else:

        form = StudyFeedbackForm()

    return render(
        request,
        "planner/feedback_form.html",
        {
            "form": form,
            "session": session,
        },
    )


@login_required
def generate_plan(request):

    if request.method != "POST":
        return redirect("planner:index")

    try:

        sessions = generate_weekly_plan(
            user=request.user,
            session_minutes=60,
        )

    except ValueError as exc:

        messages.error(
            request,
            str(exc),
        )

        return redirect("planner:index")

    if sessions:

        messages.success(
            request,
            f"{len(sessions)} جلسه مطالعه با موفقیت برای شما ایجاد شد.",
        )

    else:

        messages.warning(
            request,
            "امکان ایجاد برنامه وجود ندارد. "
            "ابتدا درس و زمان‌های آزاد خود را ثبت کنید.",
        )

    return redirect("planner:index")
