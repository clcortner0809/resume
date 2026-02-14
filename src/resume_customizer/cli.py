"""CLI interface for the resume customizer."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .bank import ResumeBank
from .customizer import customize_resume
from .pdf_generator import generate_pdf

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output"


@click.group()
@click.option(
    "--bank-dir",
    type=click.Path(exists=False, file_okay=False),
    default=None,
    help="Directory containing resume JSON files (default: ./resumes)",
)
@click.pass_context
def main(ctx: click.Context, bank_dir: str | None) -> None:
    """Resume Customizer — tailor resumes to job descriptions with LLM."""
    ctx.ensure_object(dict)
    ctx.obj["bank"] = ResumeBank(bank_dir)


# --------------------------------------------------------------------------- #
# bank commands
# --------------------------------------------------------------------------- #


@main.command("list")
@click.pass_context
def list_resumes(ctx: click.Context) -> None:
    """List all resumes in the bank."""
    bank: ResumeBank = ctx.obj["bank"]
    names = bank.list_resumes()
    if not names:
        click.echo("No resumes found. Add JSON files to the resumes/ directory.")
        return
    click.echo(f"Found {len(names)} resume(s):\n")
    for name in names:
        click.echo(f"  - {name}")


@main.command("show")
@click.argument("name")
@click.pass_context
def show_resume(ctx: click.Context, name: str) -> None:
    """Display a resume from the bank as plain text."""
    bank: ResumeBank = ctx.obj["bank"]
    try:
        resume = bank.load(name)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    click.echo(resume.to_text())


@main.command("export-pdf")
@click.argument("name")
@click.option(
    "-o", "--output",
    type=click.Path(dir_okay=False),
    default=None,
    help="Output PDF path (default: output/<name>.pdf)",
)
@click.pass_context
def export_pdf(ctx: click.Context, name: str, output: str | None) -> None:
    """Export a resume from the bank directly to PDF (no customisation)."""
    bank: ResumeBank = ctx.obj["bank"]
    try:
        resume = bank.load(name)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    out_path = Path(output) if output else DEFAULT_OUTPUT_DIR / f"{name}.pdf"
    result = generate_pdf(resume, out_path)
    click.echo(f"PDF saved to {result}")


# --------------------------------------------------------------------------- #
# customize command
# --------------------------------------------------------------------------- #


@main.command("customize")
@click.argument("name")
@click.option(
    "-j", "--job-file",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to a text file containing the job description.",
)
@click.option(
    "-o", "--output",
    type=click.Path(dir_okay=False),
    default=None,
    help="Output PDF path (default: output/<name>_customized.pdf)",
)
@click.option(
    "--save-json/--no-save-json",
    default=False,
    help="Also save the tailored resume JSON to the bank.",
)
@click.option(
    "--model",
    default="claude-sonnet-4-20250514",
    help="Anthropic model to use.",
)
@click.option(
    "--api-key",
    envvar="ANTHROPIC_API_KEY",
    default=None,
    help="Anthropic API key (default: ANTHROPIC_API_KEY env var).",
)
@click.pass_context
def customize(
    ctx: click.Context,
    name: str,
    job_file: str | None,
    output: str | None,
    save_json: bool,
    model: str,
    api_key: str | None,
) -> None:
    """Customise a resume for a specific job description and export to PDF.

    Reads the job description from --job-file or stdin.
    """
    bank: ResumeBank = ctx.obj["bank"]

    # Load base resume
    try:
        resume = bank.load(name)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    # Read job description
    if job_file:
        job_description = Path(job_file).read_text(encoding="utf-8")
    else:
        click.echo("Paste the job description below (press Ctrl-D when done):\n")
        job_description = sys.stdin.read()

    if not job_description.strip():
        click.echo("Error: empty job description.", err=True)
        sys.exit(1)

    click.echo("Customising resume with LLM...")
    tailored = customize_resume(
        resume, job_description, model=model, api_key=api_key
    )

    # Optionally save JSON
    if save_json:
        json_name = f"{name}_customized"
        bank.save(json_name, tailored)
        click.echo(f"Tailored JSON saved as '{json_name}' in the bank.")

    # Generate PDF
    out_path = (
        Path(output)
        if output
        else DEFAULT_OUTPUT_DIR / f"{name}_customized.pdf"
    )
    result = generate_pdf(tailored, out_path)
    click.echo(f"PDF saved to {result}")


if __name__ == "__main__":
    main()
