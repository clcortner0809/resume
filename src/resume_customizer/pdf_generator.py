"""Generate a professional PDF from a Resume model using fpdf2."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

from .models import Resume

# Characters outside latin-1 that the built-in Helvetica font can't render
_UNICODE_REPLACEMENTS = {
    "\u2014": "-",   # em dash
    "\u2013": "-",   # en dash
    "\u2018": "'",   # left single quote
    "\u2019": "'",   # right single quote
    "\u201c": '"',   # left double quote
    "\u201d": '"',   # right double quote
    "\u2026": "...", # ellipsis
    "\u2022": "-",   # bullet
}


def _sanitize(text: str) -> str:
    """Replace unicode chars unsupported by built-in PDF fonts."""
    for char, replacement in _UNICODE_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    return text


# Layout constants (mm)
PAGE_W = 210
MARGIN_LEFT = 15
MARGIN_RIGHT = 15
CONTENT_W = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT

# Font sizes
NAME_SIZE = 18
SECTION_HEADING_SIZE = 12
BODY_SIZE = 10
SMALL_SIZE = 9

# Colours (R, G, B)
BLACK = (0, 0, 0)
DARK_GREY = (60, 60, 60)
ACCENT = (30, 80, 160)


class ResumePDF(FPDF):
    """Custom FPDF subclass with resume-specific helpers."""

    def __init__(self) -> None:
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(MARGIN_LEFT, 15, MARGIN_RIGHT)

    # ---- helpers -----------------------------------------------------------

    def _section_heading(self, title: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", "B", SECTION_HEADING_SIZE)
        self.set_text_color(*ACCENT)
        self.cell(w=CONTENT_W, h=7, text=title.upper(), new_x="LMARGIN", new_y="NEXT")
        # Underline
        y = self.get_y()
        self.set_draw_color(*ACCENT)
        self.line(MARGIN_LEFT, y, PAGE_W - MARGIN_RIGHT, y)
        self.ln(3)

    def _body_text(self, text: str, bold: bool = False) -> None:
        style = "B" if bold else ""
        self.set_font("Helvetica", style, BODY_SIZE)
        self.set_text_color(*BLACK)
        self.multi_cell(w=CONTENT_W, h=5, text=_sanitize(text))

    def _small_text(self, text: str, italic: bool = False) -> None:
        style = "I" if italic else ""
        self.set_font("Helvetica", style, SMALL_SIZE)
        self.set_text_color(*DARK_GREY)
        self.multi_cell(w=CONTENT_W, h=4.5, text=_sanitize(text))

    def _bullet(self, text: str) -> None:
        self.set_font("Helvetica", "", BODY_SIZE)
        self.set_text_color(*BLACK)
        bullet_indent = 5
        self.set_x(MARGIN_LEFT + bullet_indent)
        # Use a dash as bullet since standard fonts lack bullet char
        self.multi_cell(w=CONTENT_W - bullet_indent, h=5, text=f"- {_sanitize(text)}")


def generate_pdf(resume: Resume, output_path: Path | str) -> Path:
    """Render a Resume as a professional PDF.

    Args:
        resume: The resume data to render.
        output_path: Where to write the PDF file.

    Returns:
        The resolved output path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pdf = ResumePDF()
    pdf.add_page()

    # ---- Contact / Header --------------------------------------------------
    pdf.set_font("Helvetica", "B", NAME_SIZE)
    pdf.set_text_color(*BLACK)
    pdf.cell(
        w=CONTENT_W, h=10, text=_sanitize(resume.contact.name), align="C",
        new_x="LMARGIN", new_y="NEXT",
    )

    contact_parts = [
        p
        for p in [
            resume.contact.email,
            resume.contact.phone,
            resume.contact.location,
            resume.contact.linkedin,
            resume.contact.website,
        ]
        if p
    ]
    if contact_parts:
        pdf.set_font("Helvetica", "", SMALL_SIZE)
        pdf.set_text_color(*DARK_GREY)
        pdf.cell(
            w=CONTENT_W, h=5, text=_sanitize("  |  ".join(contact_parts)), align="C",
            new_x="LMARGIN", new_y="NEXT",
        )
    pdf.ln(2)

    # ---- Summary -----------------------------------------------------------
    if resume.summary:
        pdf._section_heading("Summary")
        pdf._body_text(resume.summary)
        pdf.ln(1)

    # ---- Experience --------------------------------------------------------
    if resume.experience:
        pdf._section_heading("Experience")
        for exp in resume.experience:
            date_range = ""
            if exp.start_date:
                date_range = f"{exp.start_date} - {exp.end_date or 'Present'}"
            pdf._body_text(f"{exp.title}  -  {exp.company}", bold=True)
            meta = " | ".join(p for p in [exp.location, date_range] if p)
            if meta:
                pdf._small_text(meta, italic=True)
            for bullet in exp.bullets:
                pdf._bullet(bullet)
            pdf.ln(2)

    # ---- Education ---------------------------------------------------------
    if resume.education:
        pdf._section_heading("Education")
        for edu in resume.education:
            pdf._body_text(f"{edu.degree}  -  {edu.institution}", bold=True)
            meta = " | ".join(
                p for p in [edu.location, edu.graduation_date] if p
            )
            if meta:
                pdf._small_text(meta, italic=True)
            if edu.gpa:
                pdf._small_text(f"GPA: {edu.gpa}")
            for detail in edu.details:
                pdf._bullet(detail)
            pdf.ln(2)

    # ---- Skills ------------------------------------------------------------
    if resume.skills:
        pdf._section_heading("Skills")
        pdf._body_text(", ".join(resume.skills))
        pdf.ln(1)

    # ---- Projects ----------------------------------------------------------
    if resume.projects:
        pdf._section_heading("Projects")
        for proj in resume.projects:
            pdf._body_text(proj.name, bold=True)
            if proj.description:
                pdf._small_text(proj.description)
            if proj.technologies:
                pdf._small_text(f"Technologies: {', '.join(proj.technologies)}")
            for bullet in proj.bullets:
                pdf._bullet(bullet)
            pdf.ln(2)

    # ---- Certifications ----------------------------------------------------
    if resume.certifications:
        pdf._section_heading("Certifications")
        for cert in resume.certifications:
            parts = [cert.name]
            if cert.issuer:
                parts.append(cert.issuer)
            if cert.date:
                parts.append(cert.date)
            pdf._body_text(" - ".join(parts))
        pdf.ln(1)

    pdf.output(str(output_path))
    return output_path.resolve()
