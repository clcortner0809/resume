"""Tests for the LLM customizer (mocked — no real API calls)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from resume_customizer.customizer import customize_resume
from resume_customizer.models import ContactInfo, Experience, Resume


def _base_resume() -> Resume:
    return Resume(
        contact=ContactInfo(name="Test User", email="test@test.com"),
        summary="A generic summary.",
        experience=[
            Experience(
                title="Engineer",
                company="Acme",
                bullets=["Did engineering work"],
            ),
        ],
        skills=["Python", "SQL"],
    )


def _fake_api_response(resume_json: str) -> MagicMock:
    """Build a mock Anthropic messages.create response."""
    msg = MagicMock()
    block = MagicMock()
    block.text = resume_json
    msg.content = [block]
    return msg


class TestCustomizeResume:
    @patch("resume_customizer.customizer.anthropic.Anthropic")
    def test_returns_tailored_resume(self, mock_anthropic_cls: MagicMock) -> None:
        base = _base_resume()

        tailored_data = base.model_dump()
        tailored_data["summary"] = "Tailored summary for the target role."
        tailored_data["skills"] = ["SQL", "Python"]  # reordered

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _fake_api_response(
            json.dumps(tailored_data)
        )
        mock_anthropic_cls.return_value = mock_client

        result = customize_resume(base, "We need a SQL expert.", api_key="fake-key")

        assert isinstance(result, Resume)
        assert result.summary == "Tailored summary for the target role."
        assert result.skills == ["SQL", "Python"]

    @patch("resume_customizer.customizer.anthropic.Anthropic")
    def test_strips_markdown_fences(self, mock_anthropic_cls: MagicMock) -> None:
        base = _base_resume()
        tailored_data = base.model_dump()

        # Simulate model wrapping JSON in markdown fences
        fenced = f"```json\n{json.dumps(tailored_data)}\n```"

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _fake_api_response(fenced)
        mock_anthropic_cls.return_value = mock_client

        result = customize_resume(base, "Job description here.", api_key="fake-key")
        assert isinstance(result, Resume)
        assert result.contact.name == "Test User"

    @patch("resume_customizer.customizer.anthropic.Anthropic")
    def test_passes_model_param(self, mock_anthropic_cls: MagicMock) -> None:
        base = _base_resume()
        tailored_data = base.model_dump()

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _fake_api_response(
            json.dumps(tailored_data)
        )
        mock_anthropic_cls.return_value = mock_client

        customize_resume(
            base, "Job desc.", model="claude-haiku-4-5-20251001", api_key="fake-key"
        )

        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs.kwargs["model"] == "claude-haiku-4-5-20251001"

    @patch("resume_customizer.customizer.anthropic.Anthropic")
    def test_raises_on_invalid_json(self, mock_anthropic_cls: MagicMock) -> None:
        base = _base_resume()

        mock_client = MagicMock()
        mock_client.messages.create.return_value = _fake_api_response(
            "This is not valid JSON at all"
        )
        mock_anthropic_cls.return_value = mock_client

        with pytest.raises(json.JSONDecodeError):
            customize_resume(base, "Job desc.", api_key="fake-key")
