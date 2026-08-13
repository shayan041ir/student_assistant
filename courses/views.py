from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Course
from .forms import CourseForm


@login_required
def course_list(request):

    courses = Course.objects.filter(user=request.user).order_by("exam_date")

    return render(request, "courses/list.html", {"courses": courses})


@login_required
def course_detail(request, pk):

    course = get_object_or_404(Course, pk=pk, user=request.user)

    return render(request, "courses/detail.html", {"course": course})


@login_required
def course_create(request):

    if request.method == "POST":

        form = CourseForm(request.POST)

        if form.is_valid():

            course = form.save(commit=False)

            # درس متعلق به کاربر فعلی
            course.user = request.user

            course.save()

            messages.success(request, "درس با موفقیت ایجاد شد.")

            return redirect("courses:list")

    else:

        form = CourseForm()

    return render(request, "courses/form.html", {"form": form, "title": "افزودن درس"})


@login_required
def course_update(request, pk):

    course = get_object_or_404(Course, pk=pk, user=request.user)

    if request.method == "POST":

        form = CourseForm(request.POST, instance=course)

        if form.is_valid():

            form.save()

            messages.success(request, "درس با موفقیت ویرایش شد.")

            return redirect("courses:list")

    else:

        form = CourseForm(instance=course)

    return render(request, "courses/form.html", {"form": form, "title": "ویرایش درس"})


@login_required
def course_delete(request, pk):

    course = get_object_or_404(Course, pk=pk, user=request.user)

    if request.method == "POST":

        course.delete()

        messages.success(request, "درس با موفقیت حذف شد.")

        return redirect("courses:list")

    return render(request, "courses/delete.html", {"course": course})
