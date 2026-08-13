from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Note
from .forms import NoteForm


@login_required
def note_list(request):

    notes = (
        Note.objects.filter(user=request.user)
        .select_related("course")
        .order_by("-created_at")
    )

    return render(request, "notes/list.html", {"notes": notes})


@login_required
def note_create(request):

    if request.method == "POST":

        form = NoteForm(request.POST)

        # فقط درس‌های متعلق به کاربر
        form.fields["course"].queryset = request.user.courses.all()

        if form.is_valid():

            note = form.save(commit=False)

            note.user = request.user

            note.save()

            messages.success(request, "نوت با موفقیت ایجاد شد.")

            return redirect("notes:list")

    else:

        form = NoteForm()

        form.fields["course"].queryset = request.user.courses.all()

    return render(request, "notes/form.html", {"form": form, "title": "افزودن نوت"})


@login_required
def note_update(request, pk):

    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == "POST":

        form = NoteForm(request.POST, instance=note)

        form.fields["course"].queryset = request.user.courses.all()

        if form.is_valid():

            form.save()

            messages.success(request, "نوت با موفقیت ویرایش شد.")

            return redirect("notes:list")

    else:

        form = NoteForm(instance=note)

        form.fields["course"].queryset = request.user.courses.all()

    return render(request, "notes/form.html", {"form": form, "title": "ویرایش نوت"})


@login_required
def note_delete(request, pk):

    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == "POST":

        note.delete()

        messages.success(request, "نوت حذف شد.")

        return redirect("notes:list")

    return render(request, "notes/delete.html", {"note": note})


@login_required
def note_detail(request, pk):

    note = get_object_or_404(Note, pk=pk, user=request.user)

    return render(request, "notes/detail.html", {"note": note})
