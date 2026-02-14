"""Tests for resume data models."""

from resume_customizer.models import (
    Certification,
    ContactInfo,
    Education,
    Experience,
    Project,
    Resume,
)


def _make_minimal_resume() -> Resume:
    return Resume(contact=ContactInfo(name="Test User"))


def _make_full_resume() -> Resume:
    return Resume(
        contact=ContactInfo(
            name="Jane Doe",
            email="jane@example.com",
            phone="555-0100",
            location="Seattle, WA",
        ),
        summary="Experienced engineer.",
        experience=[
            Experience(
                title="Engineer",
                company="Acme",
                start_date="Jan 2020",
                end_date="Present",
                bullets=["Built things", "Fixed things"],
            ),
        ],
        education=[
            Education(
                degree="B.S. Computer Science",
                institution="State University",
                graduation_date="2019",
                gpa="3.5",
                details=["Honors"],
            ),
        ],
        skills=["Python", "Go"],
        projects=[
            Project(
                name="Widget",
                description="A widget",
                technologies=["Python"],
                bullets=["Did stuff"],
            ),
        ],
        certifications=[
            Certification(name="AWS SAA", issuer="AWS", date="2023"),
        ],
    )


class TestContactInfo:
    def test_minimal(self) -> None:
        c = ContactInfo(name="Alice")
        assert c.name == "Alice"
        assert c.email == ""

    def test_full(self) -> None:
        c = ContactInfo(
            name="Alice",
            email="a@b.com",
            phone="123",
            location="NY",
            linkedin="li",
            website="w",
        )
        assert c.email == "a@b.com"


class TestResume:
    def test_minimal_resume(self) -> None:
        r = _make_minimal_resume()
        assert r.contact.name == "Test User"
        assert r.experience == []

    def test_roundtrip_json(self) -> None:
        r = _make_full_resume()
        data = r.model_dump()
        r2 = Resume.model_validate(data)
        assert r == r2

    def test_to_text_contains_name(self) -> None:
        r = _make_full_resume()
        text = r.to_text()
        assert "Jane Doe" in text
        assert "EXPERIENCE" in text
        assert "EDUCATION" in text
        assert "SKILLS" in text
        assert "Python" in text

    def test_to_text_minimal(self) -> None:
        r = _make_minimal_resume()
        text = r.to_text()
        assert "Test User" in text
        # No section headers for empty sections
        assert "EXPERIENCE" not in text
