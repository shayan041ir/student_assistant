from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from notes.models import Note

from .forms import AIQuestionForm
from .models import AIHistory
from .services.openai_service import OpenAIService


@login_required
def ask_note(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id,
        user=request.user,
    )

    if request.method == "POST":

        form = AIQuestionForm(request.POST)

        if form.is_valid():

            question = form.cleaned_data["question"]

            selected_text = form.cleaned_data["selected_text"]

            context = selected_text.strip() if selected_text.strip() else note.content

            try:

                service = OpenAIService()

                answer = service.ask(
                    question=question,
                    context=context,
                )

                AIHistory.objects.create(
                    user=request.user,
                    note=note,
                    question=question,
                    answer=answer,
                )

                return render(
                    request,
                    "ai/answer.html",
                    {
                        "note": note,
                        "question": question,
                        "answer": answer,
                        "selected_text": selected_text,
                    },
                )

            except Exception as exc:

                messages.error(request, "خطا در ارتباط با سرویس هوش مصنوعی.")

    else:

        form = AIQuestionForm()

    return render(
        request,
        "ai/ask.html",
        {
            "note": note,
            "form": form,
        },
    )


@login_required
def summarize_note(request, note_id):

    note = get_object_or_404(
        Note,
        id=note_id,
        user=request.user,
    )

    if request.method != "POST":

        return redirect("notes:detail", pk=note.id)

    try:

        service = OpenAIService()

        summary = service.summarize(note.content)

        AIHistory.objects.create(
            user=request.user,
            note=note,
            question="خلاصه‌سازی نوت",
            answer=summary,
        )

        return render(
            request,
            "ai/summary.html",
            {
                "note": note,
                "summary": summary,
            },
        )

    except Exception:

        messages.error(request, "خطا در خلاصه‌سازی نوت.")

        return redirect("notes:detail", pk=note.id)
