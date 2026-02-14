"""LLM-powered resume customization using the Anthropic API."""

from __future__ import annotations

import json

import anthropic

from .models import Resume

SYSTEM_PROMPT = """\
You are an expert resume writer and career coach. Your job is to take an \
existing resume and tailor it to a specific job description.

Rules:
1. Keep all information truthful — never fabricate experience, skills, or credentials.
2. Rewrite the summary to target the role described in the job posting.
3. Reorder and rephrase experience bullets to emphasise the most relevant \
   accomplishments for this role.
4. Adjust skill ordering so the most relevant skills appear first.
5. Drop bullets or skills that are clearly irrelevant, but keep the overall \
   resume substantial.
6. Use strong action verbs and quantify achievements where possible.
7. Keep the tone professional and concise.

Return ONLY a valid JSON object matching the resume schema — no markdown \
fences, no commentary. The schema has these top-level keys:
  contact, summary, experience, education, skills, projects, certifications.
"""


def customize_resume(
    resume: Resume,
    job_description: str,
    *,
    model: str = "claude-sonnet-4-20250514",
    api_key: str | None = None,
) -> Resume:
    """Send the resume + job description to the LLM and return a tailored Resume.

    Args:
        resume: The base resume to customise.
        job_description: The full text of the job posting.
        model: Anthropic model ID to use.
        api_key: Optional API key (falls back to ANTHROPIC_API_KEY env var).

    Returns:
        A new Resume instance with content tailored to the job description.
    """
    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    user_message = (
        f"Here is the candidate's current resume:\n\n"
        f"```json\n{resume.model_dump_json(indent=2)}\n```\n\n"
        f"Here is the job description to tailor the resume for:\n\n"
        f"---\n{job_description}\n---\n\n"
        f"Please return the tailored resume as a JSON object."
    )

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text.strip()

    # Strip markdown code fences if the model includes them despite instructions
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [l for l in lines[1:] if l.strip() != "```"]
        raw_text = "\n".join(lines)

    data = json.loads(raw_text)
    return Resume.model_validate(data)
