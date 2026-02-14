"""Tests for the resume bank."""

import json
from pathlib import Path

import pytest

from resume_customizer.bank import ResumeBank
from resume_customizer.models import ContactInfo, Resume


@pytest.fixture()
def tmp_bank(tmp_path: Path) -> ResumeBank:
    return ResumeBank(tmp_path)


@pytest.fixture()
def sample_resume() -> Resume:
    return Resume(
        contact=ContactInfo(name="Test Person", email="test@example.com"),
        summary="A test resume.",
        skills=["Python", "Testing"],
    )


class TestResumeBank:
    def test_list_empty(self, tmp_bank: ResumeBank) -> None:
        assert tmp_bank.list_resumes() == []

    def test_save_and_load(
        self, tmp_bank: ResumeBank, sample_resume: Resume
    ) -> None:
        tmp_bank.save("test", sample_resume)
        loaded = tmp_bank.load("test")
        assert loaded.contact.name == "Test Person"
        assert loaded.skills == ["Python", "Testing"]

    def test_list_after_save(
        self, tmp_bank: ResumeBank, sample_resume: Resume
    ) -> None:
        tmp_bank.save("alpha", sample_resume)
        tmp_bank.save("beta", sample_resume)
        names = tmp_bank.list_resumes()
        assert names == ["alpha", "beta"]

    def test_load_missing_raises(self, tmp_bank: ResumeBank) -> None:
        with pytest.raises(FileNotFoundError):
            tmp_bank.load("nonexistent")

    def test_load_all(
        self, tmp_bank: ResumeBank, sample_resume: Resume
    ) -> None:
        tmp_bank.save("one", sample_resume)
        tmp_bank.save("two", sample_resume)
        all_resumes = tmp_bank.load_all()
        assert set(all_resumes.keys()) == {"one", "two"}

    def test_saved_file_is_valid_json(
        self, tmp_bank: ResumeBank, sample_resume: Resume
    ) -> None:
        path = tmp_bank.save("check", sample_resume)
        data = json.loads(path.read_text())
        assert data["contact"]["name"] == "Test Person"
