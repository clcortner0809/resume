"""Tests for PDF generation."""

from pathlib import Path

from resume_customizer.models import (
    ContactInfo,
    Education,
    Experience,
    Resume,
)
from resume_customizer.pdf_generator import generate_pdf


def _make_resume() -> Resume:
    return Resume(
        contact=ContactInfo(
            name="PDF Test",
            email="pdf@test.com",
            phone="555-0000",
            location="Testville",
        ),
        summary="A summary for PDF testing.",
        experience=[
            Experience(
                title="Developer",
                company="TestCo",
                start_date="2020",
                end_date="2023",
                bullets=["Wrote code", "Reviewed PRs"],
            ),
        ],
        education=[
            Education(
                degree="B.S. CS",
                institution="Test University",
                graduation_date="2019",
            ),
        ],
        skills=["Python", "Testing", "PDF"],
    )


class TestPDFGeneration:
    def test_generates_file(self, tmp_path: Path) -> None:
        resume = _make_resume()
        out = tmp_path / "test.pdf"
        result = generate_pdf(resume, out)
        assert result.exists()
        assert result.stat().st_size > 0

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        resume = _make_resume()
        out = tmp_path / "sub" / "dir" / "test.pdf"
        result = generate_pdf(resume, out)
        assert result.exists()

    def test_pdf_starts_with_magic(self, tmp_path: Path) -> None:
        resume = _make_resume()
        out = tmp_path / "magic.pdf"
        generate_pdf(resume, out)
        content = out.read_bytes()
        assert content[:5] == b"%PDF-"

    def test_minimal_resume_pdf(self, tmp_path: Path) -> None:
        resume = Resume(contact=ContactInfo(name="Minimal"))
        out = tmp_path / "minimal.pdf"
        result = generate_pdf(resume, out)
        assert result.exists()
