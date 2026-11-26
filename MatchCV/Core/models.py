from django.conf import settings
from django.db import models



class CV(models.Model):
    """An original CV, exactly as the user uploaded or pasted it.

    Original uploads are raw material only. They are never matched against a
    role: matching always runs on an TailoredCV built from one of these.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cvs"
    )
    title = models.CharField(max_length=160)
    file = models.FileField(upload_to="cvs/", blank=True)
    text_content = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title

    def read_text(self):
        """Plain text of the CV: pasted text, or extracted from the PDF/DOCX file."""
        if self.text_content.strip():
            return self.text_content
        if not self.file:
            return ""
        name = self.file.name.lower()
        try:
            if name.endswith(".pdf"):
                import pdfplumber

                with pdfplumber.open(self.file.path) as pdf:
                    return "\n".join(page.extract_text() or "" for page in pdf.pages)
            if name.endswith(".docx"):
                import docx

                document = docx.Document(self.file.path)
                return "\n".join(paragraph.text for paragraph in document.paragraphs)
        except Exception:
            return ""
        return ""


class TailoredCV(models.Model):
    """A polished, general-purpose version of an original CV.

    This is the only kind of CV that can be matched against a role.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enhanced_cvs"
    )
    source = models.ForeignKey(
        CV, on_delete=models.CASCADE, related_name="enhanced_versions"
    )
    title = models.CharField(max_length=160)
    headline = models.CharField(max_length=220, blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField(help_text="The polished CV in markdown")
    improvements = models.JSONField(default=list, blank=True)
    strengths = models.JSONField(default=list, blank=True)
    gaps_left = models.JSONField(default=list, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Match(models.Model):
    """One role analysis, run against a saved enhanced CV."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="matches"
    )
    cv = models.ForeignKey(
        TailoredCV, on_delete=models.CASCADE, related_name="matches"
    )
    job_title = models.CharField(max_length=160)
    company = models.CharField(max_length=160, blank=True)
    job_description = models.TextField()
    overall_score = models.PositiveSmallIntegerField(default=0)
    verdict = models.CharField(max_length=40, blank=True)
    summary = models.TextField(blank=True)
    fit_evidence = models.JSONField(default=list, blank=True)
    matched_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    strengths = models.JSONField(default=list, blank=True)
    critique = models.JSONField(default=list, blank=True)
    keyword_gaps = models.JSONField(default=list, blank=True)
    experience_gaps = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.job_title
