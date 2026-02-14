"""Data models for resumes."""

from __future__ import annotations

from pydantic import BaseModel


class ContactInfo(BaseModel):
    name: str
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    website: str = ""


class Experience(BaseModel):
    title: str
    company: str
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    bullets: list[str] = []


class Education(BaseModel):
    degree: str
    institution: str
    location: str = ""
    graduation_date: str = ""
    gpa: str = ""
    details: list[str] = []


class Project(BaseModel):
    name: str
    description: str = ""
    technologies: list[str] = []
    bullets: list[str] = []


class Certification(BaseModel):
    name: str
    issuer: str = ""
    date: str = ""


class Resume(BaseModel):
    """A complete resume with all sections."""

    contact: ContactInfo
    summary: str = ""
    experience: list[Experience] = []
    education: list[Education] = []
    skills: list[str] = []
    projects: list[Project] = []
    certifications: list[Certification] = []

    def to_text(self) -> str:
        """Render resume as plain text for LLM context."""
        lines: list[str] = []

        # Contact
        lines.append(self.contact.name)
        contact_parts = [
            p
            for p in [
                self.contact.email,
                self.contact.phone,
                self.contact.location,
                self.contact.linkedin,
                self.contact.website,
            ]
            if p
        ]
        if contact_parts:
            lines.append(" | ".join(contact_parts))
        lines.append("")

        # Summary
        if self.summary:
            lines.append("SUMMARY")
            lines.append(self.summary)
            lines.append("")

        # Experience
        if self.experience:
            lines.append("EXPERIENCE")
            for exp in self.experience:
                date_range = ""
                if exp.start_date:
                    date_range = f"{exp.start_date} - {exp.end_date or 'Present'}"
                lines.append(f"{exp.title} at {exp.company}")
                if exp.location or date_range:
                    lines.append(
                        " | ".join(p for p in [exp.location, date_range] if p)
                    )
                for bullet in exp.bullets:
                    lines.append(f"  - {bullet}")
                lines.append("")

        # Education
        if self.education:
            lines.append("EDUCATION")
            for edu in self.education:
                lines.append(f"{edu.degree} - {edu.institution}")
                if edu.location or edu.graduation_date:
                    lines.append(
                        " | ".join(
                            p for p in [edu.location, edu.graduation_date] if p
                        )
                    )
                if edu.gpa:
                    lines.append(f"  GPA: {edu.gpa}")
                for detail in edu.details:
                    lines.append(f"  - {detail}")
                lines.append("")

        # Skills
        if self.skills:
            lines.append("SKILLS")
            lines.append(", ".join(self.skills))
            lines.append("")

        # Projects
        if self.projects:
            lines.append("PROJECTS")
            for proj in self.projects:
                lines.append(proj.name)
                if proj.description:
                    lines.append(f"  {proj.description}")
                if proj.technologies:
                    lines.append(f"  Technologies: {', '.join(proj.technologies)}")
                for bullet in proj.bullets:
                    lines.append(f"  - {bullet}")
                lines.append("")

        # Certifications
        if self.certifications:
            lines.append("CERTIFICATIONS")
            for cert in self.certifications:
                parts = [cert.name]
                if cert.issuer:
                    parts.append(cert.issuer)
                if cert.date:
                    parts.append(cert.date)
                lines.append(" - ".join(parts))
            lines.append("")

        return "\n".join(lines)
