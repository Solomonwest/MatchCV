"""The two AI passes: general enhancement, then role analysis.

Both are grounded in the CV text they are given. Neither may invent an
employer, date, qualification, tool, metric or achievement.
"""

from .ai import AIError, complete_json, object_list, score, string_list, text


def profile_block(profile_text):
    """The candidate's own profile, offered as context and never as evidence."""
    if not (profile_text or "").strip():
        return ""
    return (
        "CANDIDATE PROFILE (supplied by the candidate themselves; you may use it "
        "for contact details and for the direction they want, but never invent "
        "experience, employers, dates or qualifications from it):\n"
        "\"\"\"\n" + profile_text.strip()[:2000] + "\n\"\"\"\n\n"
    )


ENHANCE_SYSTEM = """You are a senior CV writer. You improve how a candidate's
existing CV reads, without ever inventing anything.

Hard rules:
- Use only facts that appear in the CV you are given. Never add employers, job
  titles, dates, qualifications, tools, metrics, awards or achievements that are
  not already there.
- You may reorder, regroup, reword, tighten and reformat. You may not add claims.
- Where the CV is vague, keep it vague rather than inventing specifics.
- This version is general purpose: do not target any particular job description.
- Follow the CV's own spelling convention and keep its language.

Reply with one JSON object with exactly these keys:
{
  "title": "a short label for this CV, for example Product Designer CV",
  "headline": "the candidate's professional title line",
  "summary": "a 2-3 sentence professional summary built only from what the CV shows",
  "content": "the complete polished CV in markdown",
  "improvements": [{"what": "the change you made", "why": "the problem it fixes"}],
  "strengths": ["what already works well in this CV"],
  "gaps_left": ["information the CV lacks that a reader would expect"]
}

content must be a complete CV in markdown: the candidate's name and contact
details when present, then a summary, a core skills list, experience with
achievement bullets, and education. Use ## headings and bullet lists.
improvements: 3-6 items. strengths: 3-5 short lines. gaps_left: up to 5 short
lines, phrased as things the candidate can add if they are true.
No emojis. No flattery."""

ANALYSE_SYSTEM = """You are an expert recruiter and CV analyst. Judge how well
this already-polished CV fits one specific role, and critique the CV itself.

Hard rules:
- Judge only on what the CV shows. Never assume unstated experience.
- Distinguish "not evidenced in the CV" from "the candidate lacks it". Say which
  one you mean in every gap you list.
- Be honest rather than encouraging. A high score must be earned.
- No emojis, no flattery, no hedging.

Reply with one JSON object with exactly these keys:
{
  "overall_score": 0-100,
  "verdict": "Strong match" or "Good match" or "Partial match" or "Stretch",
  "summary": "2-3 direct sentences on the fit",
  "fit_evidence": [{"requirement": "a must-have from the description", "evidence": "the CV line that satisfies it, or Not evidenced"}],
  "matched_skills": ["concrete skills, tools or domains the CV demonstrably shows"],
  "missing_skills": [{"skill": "the requirement", "priority": "Critical or Important or Nice to have", "how_to_close": "one practical sentence"}],
  "strengths": ["what makes this CV competitive for this role"],
  "critique": [{"area": "Structure", "rating": "Strong or Adequate or Weak", "note": "one or two sentences"}],
  "keyword_gaps": ["exact terms from the description that the CV never uses"],
  "experience_gaps": ["depth, scope, seniority or industry context the role expects and the CV does not show"],
  "recommendations": ["concrete actions before applying, most impactful first"]
}

fit_evidence: up to 8 of the role's most important requirements.
matched_skills: max 12, most important first.
missing_skills: max 8, most important first.
strengths: 3-5. keyword_gaps: max 10. experience_gaps: max 5.
critique: exactly four items, one for each area in this order: Structure,
Clarity, Impact, Credibility.
recommendations: 3-5, each one sentence and specific to this CV."""


def enhance_cv(cv_text, profile_text=""):
    """Turn an original CV into one polished, general-purpose CV."""
    prompt = (
        "Rewrite this CV into one polished, general-purpose version.\n\n"
        + profile_block(profile_text)
        + "CV TEXT:\n\"\"\"\n" + cv_text.strip()[:24000] + "\n\"\"\""
    )
    data = complete_json(
        ENHANCE_SYSTEM,
        prompt,
        ["title", "headline", "summary", "content", "improvements", "strengths", "gaps_left"],
    )

    content = text(data.get("content"), 30000)
    if not content:
        raise AIError("The model returned an empty CV. Please try again.")

    return {
        "title": text(data.get("title"), 160) or "Enhanced CV",
        "headline": text(data.get("headline"), 220),
        "summary": text(data.get("summary"), 2000),
        "content": content,
        "improvements": object_list(data.get("improvements"), ["what", "why"], 8),
        "strengths": string_list(data.get("strengths"), 6),
        "gaps_left": string_list(data.get("gaps_left"), 6),
    }


VERDICTS = ["Strong match", "Good match", "Partial match", "Stretch"]


def _verdict(value, overall_score):
    label = str(value or "").strip()
    if label in VERDICTS:
        return label
    number = score(overall_score)
    if number >= 80:
        return "Strong match"
    if number >= 60:
        return "Good match"
    if number >= 40:
        return "Partial match"
    return "Stretch"


def analyse(enhanced_text, job_title, company, job_description, profile_text=""):
    """Score one enhanced CV against one job description."""
    prompt = (
        profile_block(profile_text)
        + "JOB TITLE: " + job_title + "\n"
        "COMPANY: " + (company or "Not specified") + "\n\n"
        "JOB DESCRIPTION:\n\"\"\"\n" + job_description.strip()[:20000] + "\n\"\"\"\n\n"
        "CANDIDATE CV:\n\"\"\"\n" + enhanced_text.strip()[:24000] + "\n\"\"\""
    )
    data = complete_json(
        ANALYSE_SYSTEM,
        prompt,
        [
            "overall_score",
            "verdict",
            "summary",
            "fit_evidence",
            "matched_skills",
            "missing_skills",
            "strengths",
            "critique",
            "keyword_gaps",
            "experience_gaps",
            "recommendations",
        ],
    )

    return {
        "overall_score": score(data.get("overall_score")),
        "verdict": _verdict(data.get("verdict"), data.get("overall_score")),
        "summary": text(data.get("summary"), 2000),
        "fit_evidence": object_list(
            data.get("fit_evidence"), ["requirement", "evidence"], 10
        ),
        "matched_skills": string_list(data.get("matched_skills"), 12),
        "missing_skills": object_list(
            data.get("missing_skills"), ["skill", "priority", "how_to_close"], 10
        ),
        "strengths": string_list(data.get("strengths"), 6),
        "critique": object_list(data.get("critique"), ["area", "rating", "note"], 6),
        "keyword_gaps": string_list(data.get("keyword_gaps"), 12),
        "experience_gaps": string_list(data.get("experience_gaps"), 8),
        "recommendations": string_list(data.get("recommendations"), 6),
    }