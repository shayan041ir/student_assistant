from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import StudySession
from .forms import StudySessionForm, Availability, StudyFeedbackForm, AvailabilityForm


@login_required
def index(request):

    sessions = StudySession.objects.filter(user=request.user).select_related("course")

    return render(request, "planner/index.html", {"sessions": sessions})


@login_required
def create_session(request):

    if request.method == "POST":

        form = StudySessionForm(request.POST)

        form.fields["course"].queryset = request.user.courses.all()

        if form.is_valid():

            session = form.save(commit=False)

            session.user = request.user

            session.save()

            messages.success(request, "جلسه مطالعه با موفقیت ایجاد شد.")

            return redirect("planner:index")

    else:

        form = StudySessionForm()

        form.fields["course"].queryset = request.user.courses.all()

    return render(
        request, "planner/form.html", {"form": form, "title": "افزودن جلسه مطالعه"}
    )


@login_required
def update_session(request, pk):

    session = get_object_or_404(StudySession, pk=pk, user=request.user)

    if request.method == "POST":

        form = StudySessionForm(request.POST, instance=session)

        form.fields["course"].queryset = request.user.courses.all()

        if form.is_valid():

            form.save()

            messages.success(request, "جلسه مطالعه با موفقیت ویرایش شد.")

            return redirect("planner:index")

    else:

        form = StudySessionForm(instance=session)

        form.fields["course"].queryset = request.user.courses.all()

    return render(
        request, "planner/form.html", {"form": form, "title": "ویرایش جلسه مطالعه"}
    )


@login_required
def delete_session(request, pk):

    session = get_object_or_404(StudySession, pk=pk, user=request.user)

    if request.method == "POST":

        session.delete()

        messages.success(request, "جلسه مطالعه حذف شد.")

        return redirect("planner:index")

    return render(request, "planner/delete.html", {"session": session})


@login_required
def complete_session(request, pk):

    session = get_object_or_404(StudySession, pk=pk, user=request.user)

    session.status = "completed"

    session.save(update_fields=["status"])

    messages.success(request, "جلسه مطالعه به عنوان انجام‌شده ثبت شد.")

    return redirect("planner:index")


@login_required
def availability_list(request):

    availabilities = Availability.objects.filter(user=request.user)

    return render(
        request, "planner/availability_list.html", {"availabilities": availabilities}
    )


@login_required
def availability_create(request):

    if request.method == "POST":

        form = AvailabilityForm(request.POST)

        if form.is_valid():

            availability = form.save(commit=False)

            availability.user = request.user

            availability.save()

            messages.success(request, "زمان آزاد با موفقیت اضافه شد.")

            return redirect("planner:availability_list")

    else:

        form = AvailabilityForm()

    return render(
        request,
        "planner/availability_form.html",
        {"form": form, "title": "افزودن زمان آزاد"},
    )


@login_required
def create_feedback(request, pk):

    session = get_object_or_404(StudySession, pk=pk, user=request.user)

    if session.status != "completed":

        messages.warning(
            request, "ابتدا باید جلسه مطالعه را به عنوان انجام‌شده ثبت کنید."
        )

        return redirect("planner:index")

    if hasattr(session, "feedback"):

        messages.info(request, "برای این جلسه قبلاً بازخورد ثبت شده است.")

        return redirect("planner:index")

    if request.method == "POST":

        form = StudyFeedbackForm(request.POST)

        if form.is_valid():

            feedback = form.save(commit=False)

            feedback.session = session

            feedback.save()

            messages.success(request, "بازخورد جلسه با موفقیت ثبت شد.")

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
