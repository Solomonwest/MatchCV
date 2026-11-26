from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.forms import CVForm, MatchForm

from .ai import AIError

from .models import CV,  TailoredCV, Match
from .services import analyse, enhance_cv

from django.http import HttpResponse
from django.utils.text import slugify

from .pdf import build_cv_pdf

def _enhance_original(user, cv):
    """Enhance an original CV and save it to the user's profile."""
    source_text = cv.read_text()
    if not source_text.strip():
        raise AIError(
            "We could not read any text from that file. Try a text-based PDF or "
            "DOCX, or paste the CV text instead."
        )

    enhanced =  TailoredCV.objects.create(
        user=user, source=cv, **enhance_cv(source_text, user.profile_context())
    )

    # The first enhanced CV becomes the default used for matching.
    if not  TailoredCV.objects.filter(user=user).exclude(pk=enhanced.pk).exists():
        TailoredCV.objects.filter(pk=enhanced.pk).update(is_default=True)
        enhanced.is_default = True
    return enhanced


@login_required
def cv_list(request):
    """The profile: saved enhanced CVs, plus the originals they came from."""
    return render(
        request,
        "cv_list.html",
        {
            "enhanced":  TailoredCV.objects.filter(user=request.user),
            "originals": CV.objects.filter(user=request.user).prefetch_related(
                "enhanced_versions"
            ),
        },
    )


@login_required
def cv_upload(request):
    """Step 1: upload an original CV and enhance it immediately."""
    form = CVForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        cv = form.save(commit=False)
        cv.user = request.user
        cv.save()
        try:
            enhanced = _enhance_original(request.user, cv)
        except AIError as exc:
            messages.error(request, str(exc))
            return redirect("cv_list")
        messages.success(request, "Your enhanced CV is ready.")
        return redirect("cv_detail", pk=enhanced.pk)

    return render(request, "cv_upload.html", {"form": form})


@login_required
def cv_enhance(request, pk):
    """Retry the enhancement for an original upload that failed."""
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    if request.method != "POST":
        return redirect("cv_list")
    try:
        enhanced = _enhance_original(request.user, cv)
    except AIError as exc:
        messages.error(request, str(exc))
        return redirect("cv_list")
    messages.success(request, "Your enhanced CV is ready.")
    return redirect("cv_detail", pk=enhanced.pk)


@login_required
def cv_detail(request, pk):
    cv = get_object_or_404( TailoredCV, pk=pk, user=request.user)
    return render(request, "cv_detail.html", {"cv": cv})


@login_required
def enhanced_default(request, pk):
    cv = get_object_or_404( TailoredCV, pk=pk, user=request.user)
    TailoredCV.objects.filter(user=request.user).update(is_default=False)
    TailoredCV.objects.filter(pk=cv.pk).update(is_default=True)
    return redirect("cv_list")


@login_required
def enhanced_delete(request, pk):
    cv = get_object_or_404( TailoredCV, pk=pk, user=request.user)
    cv.delete()
    return redirect("cv_list")


@login_required
def cv_delete(request, pk):
    cv = get_object_or_404(CV, pk=pk, user=request.user)
    cv.delete()
    return redirect("cv_list")


@login_required
def dashboard(request):
    """Step 2: analyse a saved enhanced CV against a role."""
    enhanced =  TailoredCV.objects.filter(user=request.user)

    initial = {}
    default = enhanced.filter(is_default=True).first() or enhanced.first()
    if default:
        initial["cv"] = default.pk

    form = MatchForm(request.user, request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        cv = form.cleaned_data["cv"]
        try:
            result = analyse(
                cv.content,
                form.cleaned_data["job_title"],
                form.cleaned_data["company"],
                form.cleaned_data["job_description"],
                request.user.profile_context(),
            )
        except AIError as exc:
            form.add_error(None, str(exc))
        else:
            match = Match.objects.create(
                user=request.user,
                cv=cv,
                job_title=form.cleaned_data["job_title"],
                company=form.cleaned_data["company"],
                job_description=form.cleaned_data["job_description"],
                **result,
            )
            return redirect("match_detail", pk=match.pk)

    return render(
        request,
        "dashboard.html",
        {"form": form, "enhanced": enhanced},
    )


@login_required
def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk, user=request.user)
    return render(request, "match_detail.html", {"match": match})


@login_required
def history(request):
    return render(
        request,
        "history.html",
        {"matches": Match.objects.filter(user=request.user).select_related("cv")},
    )


@login_required
def download_cv_pdf(request, pk):
    cv = get_object_or_404(TailoredCV, pk=pk, user=request.user)  # <- adjust ownership check
    pdf_bytes = build_cv_pdf(cv.content, headline=cv.headline, title=cv.title)
    filename = (slugify(cv.title) or "cv") + ".pdf"

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

