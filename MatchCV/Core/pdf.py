"""Render the enhanced CV (markdown) as a designed A4 PDF."""

import re
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer

ACCENT = colors.HexColor("#1F4E79")
INK = colors.HexColor("#222222")
MUTED = colors.HexColor("#5F6B76")
RULE = colors.HexColor("#C9D3DC")

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

STYLES = {
    "name": ParagraphStyle("name", fontName=FONT_BOLD, fontSize=24, leading=28,
                           textColor=ACCENT, spaceAfter=2),
    "headline": ParagraphStyle("headline", fontName=FONT, fontSize=12, leading=15,
                               textColor=MUTED, spaceAfter=4),
    "contact": ParagraphStyle("contact", fontName=FONT, fontSize=9, leading=12,
                              textColor=MUTED),
    "section": ParagraphStyle("section", fontName=FONT_BOLD, fontSize=11, leading=14,
                              textColor=ACCENT, spaceBefore=12, spaceAfter=2),
    "role": ParagraphStyle("role", fontName=FONT_BOLD, fontSize=10.5, leading=13.5,
                           textColor=INK, spaceBefore=6, spaceAfter=1),
    "body": ParagraphStyle("body", fontName=FONT, fontSize=10, leading=14,
                           textColor=INK, alignment=TA_LEFT, spaceAfter=3),
    "bullet": ParagraphStyle("bullet", fontName=FONT, fontSize=10, leading=14,
                             textColor=INK, leftIndent=12, bulletIndent=2, spaceAfter=1.5),
}

BULLET_RE = re.compile(r"^\s*(?:[-*\u2022])\s+(.*)")


def _inline(value):
    """Escape text, then convert the markdown inline marks ReportLab understands."""
    value = escape(value.strip())
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", value)
    value = re.sub(
        r"\[(.+?)\]\((.+?)\)",
        r'<link href="\2" color="#1F4E79">\1</link>',
        value,
    )
    return value


def build_cv_pdf(content, headline="", title="Curriculum Vitae"):
    """Return the PDF as bytes."""
    story = []
    seen_name = False
    in_header = True  # lines before the first ## heading are contact details
    headline_norm = (headline or "").strip().lower()
    section_items = []

    def flush_section():
        nonlocal section_items
        if section_items:
            # keep a heading together with its first item so it never sits alone
            story.append(KeepTogether(section_items[:3]))
            story.extend(section_items[3:])
            section_items = []

    for raw in (content or "").splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue

        if line.startswith("# ") and not seen_name:
            seen_name = True
            story.append(Paragraph(_inline(line[2:]), STYLES["name"]))
            if headline:
                story.append(Paragraph(_inline(headline), STYLES["headline"]))
            continue

        if line.startswith("## ") or line.startswith("# "):
            flush_section()
            in_header = False
            text = line.lstrip("#").strip().upper()
            section_items = [
                Paragraph(_inline(text), STYLES["section"]),
                HRFlowable(width="100%", thickness=0.8, color=RULE,
                           spaceBefore=1, spaceAfter=4),
            ]
            continue

        if line.startswith("###"):
            target = section_items if section_items else story
            target.append(Paragraph(_inline(line.lstrip("#")), STYLES["role"]))
            continue

        bullet = BULLET_RE.match(line)
        if bullet:
            flowable = Paragraph(_inline(bullet.group(1)), STYLES["bullet"], bulletText="\u2022")
        elif in_header:
            if line.strip().lower() == headline_norm:
                continue  # already shown under the name
            flowable = Paragraph(_inline(line), STYLES["contact"])
        else:
            flowable = Paragraph(_inline(line), STYLES["body"])

        (section_items if section_items else story).append(flowable)

    flush_section()

    if not story:
        story.append(Paragraph("Empty CV", STYLES["body"]))
    story.insert(0, Spacer(1, 0))

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=title,
    )

    def accent_bar(canvas, _doc):
        canvas.saveState()
        canvas.setFillColor(ACCENT)
        canvas.rect(0, A4[1] - 6 * mm, A4[0], 6 * mm, stroke=0, fill=1)
        canvas.restoreState()

    doc.build(story, onFirstPage=accent_bar)
    return buffer.getvalue()