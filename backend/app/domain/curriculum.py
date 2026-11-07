"""A curriculum mapping: which competencies a state expects by the end of a grade."""

from pathlib import Path

import yaml
from pydantic import BaseModel


class Curriculum(BaseModel):
    state: str
    subject: str
    grade: int
    title: str
    competencies: set[str]

    @classmethod
    def load(cls, path: Path) -> "Curriculum":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        competencies = {
            c
            for unit in data["units"]
            for bullet in unit["bullets"]
            for c in bullet["competencies"]
        }
        return cls(
            state=data["state"],
            subject=data["subject"],
            grade=data["grade"],
            title=data["curriculum"],
            competencies=competencies,
        )
