"""Resume bank - manage a collection of resumes stored as JSON files."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Resume

DEFAULT_BANK_DIR = Path(__file__).resolve().parent.parent.parent / "resumes"


class ResumeBank:
    """Load, list, and save resumes from a local directory."""

    def __init__(self, bank_dir: Path | str | None = None) -> None:
        self.bank_dir = Path(bank_dir) if bank_dir else DEFAULT_BANK_DIR
        self.bank_dir.mkdir(parents=True, exist_ok=True)

    def list_resumes(self) -> list[str]:
        """Return names (stems) of all resumes in the bank."""
        return sorted(p.stem for p in self.bank_dir.glob("*.json"))

    def load(self, name: str) -> Resume:
        """Load a resume by name (filename without .json extension)."""
        path = self.bank_dir / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Resume not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return Resume.model_validate(data)

    def save(self, name: str, resume: Resume) -> Path:
        """Save a resume to the bank. Returns the file path."""
        path = self.bank_dir / f"{name}.json"
        path.write_text(
            resume.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        return path

    def load_all(self) -> dict[str, Resume]:
        """Load every resume in the bank. Returns {name: Resume}."""
        return {name: self.load(name) for name in self.list_resumes()}
