"""Tests for the CLI interface."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from click.testing import CliRunner

from resume_customizer.cli import main
from resume_customizer.models import ContactInfo, Resume


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def bank_with_resume(tmp_path: Path) -> Path:
    """Create a temp bank dir with one resume in it."""
    resume = Resume(
        contact=ContactInfo(name="CLI Test", email="cli@test.com"),
        summary="A CLI test resume.",
        skills=["Python"],
    )
    path = tmp_path / "cli_person.json"
    path.write_text(resume.model_dump_json(indent=2), encoding="utf-8")
    return tmp_path


class TestListCommand:
    def test_list_empty(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(main, ["--bank-dir", str(tmp_path), "list"])
        assert result.exit_code == 0
        assert "No resumes found" in result.output

    def test_list_with_resumes(
        self, runner: CliRunner, bank_with_resume: Path
    ) -> None:
        result = runner.invoke(
            main, ["--bank-dir", str(bank_with_resume), "list"]
        )
        assert result.exit_code == 0
        assert "cli_person" in result.output
        assert "1 resume(s)" in result.output


class TestShowCommand:
    def test_show_existing(
        self, runner: CliRunner, bank_with_resume: Path
    ) -> None:
        result = runner.invoke(
            main, ["--bank-dir", str(bank_with_resume), "show", "cli_person"]
        )
        assert result.exit_code == 0
        assert "CLI Test" in result.output

    def test_show_missing(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(
            main, ["--bank-dir", str(tmp_path), "show", "nope"]
        )
        assert result.exit_code == 1
        assert "not found" in result.output


class TestExportPdfCommand:
    def test_export_pdf(
        self, runner: CliRunner, bank_with_resume: Path, tmp_path: Path
    ) -> None:
        out_pdf = tmp_path / "out.pdf"
        result = runner.invoke(
            main,
            [
                "--bank-dir", str(bank_with_resume),
                "export-pdf", "cli_person",
                "-o", str(out_pdf),
            ],
        )
        assert result.exit_code == 0
        assert out_pdf.exists()
        assert "PDF saved to" in result.output


class TestCustomizeCommand:
    @patch("resume_customizer.cli.customize_resume")
    def test_customize_with_job_file(
        self,
        mock_customize: MagicMock,
        runner: CliRunner,
        bank_with_resume: Path,
        tmp_path: Path,
    ) -> None:
        # Mock the LLM call to return the same resume
        tailored = Resume(
            contact=ContactInfo(name="CLI Test", email="cli@test.com"),
            summary="Tailored summary.",
            skills=["Python"],
        )
        mock_customize.return_value = tailored

        job_file = tmp_path / "job.txt"
        job_file.write_text("We need a Python developer.", encoding="utf-8")

        out_pdf = tmp_path / "custom.pdf"
        result = runner.invoke(
            main,
            [
                "--bank-dir", str(bank_with_resume),
                "customize", "cli_person",
                "-j", str(job_file),
                "-o", str(out_pdf),
                "--api-key", "fake-key",
            ],
        )
        assert result.exit_code == 0
        assert out_pdf.exists()
        assert "PDF saved to" in result.output
        mock_customize.assert_called_once()

    @patch("resume_customizer.cli.customize_resume")
    def test_customize_save_json(
        self,
        mock_customize: MagicMock,
        runner: CliRunner,
        bank_with_resume: Path,
        tmp_path: Path,
    ) -> None:
        tailored = Resume(
            contact=ContactInfo(name="CLI Test", email="cli@test.com"),
            summary="Tailored for saving.",
            skills=["Python"],
        )
        mock_customize.return_value = tailored

        job_file = tmp_path / "job.txt"
        job_file.write_text("Need a dev.", encoding="utf-8")

        out_pdf = tmp_path / "save.pdf"
        result = runner.invoke(
            main,
            [
                "--bank-dir", str(bank_with_resume),
                "customize", "cli_person",
                "-j", str(job_file),
                "-o", str(out_pdf),
                "--save-json",
                "--api-key", "fake-key",
            ],
        )
        assert result.exit_code == 0
        assert "Tailored JSON saved" in result.output
        saved = bank_with_resume / "cli_person_customized.json"
        assert saved.exists()
