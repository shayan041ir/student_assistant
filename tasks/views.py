from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Task
from .forms import TaskForm


@login_required
def task_list(request):

    tasks = (
        Task.objects
        .filter(user=request.user)
        .select_related("course")
        .order_by("-created_at")
    )

    return render(
        request,
        "tasks/list.html",
        {
            "tasks": tasks
        }
    )


@login_required
def task_create(request):

    if request.method == "POST":

        form = TaskForm(request.POST)

        # فقط درس‌های متعلق به کاربر
        form.fields["course"].queryset = request.user.courses.all()

        if form.is_valid():

            task = form.save(commit=False)

            task.user = request.user

            task.save()

            messages.success(
                request,
                "تکلیف با موفقیت ایجاد شد."
            )

            return redirect("tasks:list")

    else:

        form = TaskForm()

        form.fields["course"].queryset = request.user.courses.all()

    return render(
        request,
        "tasks/form.html",
        {
            "form": form,
            "title": "افزودن تکلیف"
        }
    )


@login_required
def task_detail(request, pk):

    task = get_object_or_404(
        Task,
        pk=pk,
        user=request.user
    )

    return render(
        request,
        "tasks/detail.html",
        {
            "task": task
        }
    )


@login_required
def task_update(request, pk):

    task = get_object_or_404(
        Task,
        pk=pk,
        user=request.user
    )

    if request.method == "POST":

        form = TaskForm(
            request.POST,
            instance=task
        )

        form.fields["course"].queryset = request.user.courses.all()

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "تکلیف با موفقیت ویرایش شد."
            )

            return redirect("tasks:list")

    else:

        form = TaskForm(instance=task)

        form.fields["course"].queryset = request.user.courses.all()

    return render(
        request,
        "tasks/form.html",
        {
            "form": form,
            "title": "ویرایش تکلیف"
        }
    )


@login_required
def task_delete(request, pk):

    task = get_object_or_404(
        Task,
        pk=pk,
        user=request.user
    )

    if request.method == "POST":

        task.delete()

        messages.success(
            request,
            "تکلیف با موفقیت حذف شد."
        )

        return redirect("tasks:list")

    return render(
        request,
        "tasks/delete.html",
        {
            "task": task
        }
    )

