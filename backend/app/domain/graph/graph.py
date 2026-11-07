"""Competency graph: load content YAML, validate prerequisites, answer structure questions."""

from collections.abc import Iterator
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class BktParams(BaseModel):
    p_init: float
    p_learn: float
    p_slip: float
    p_guess: float


Area = Literal["numbers_operations", "space_shape", "quantities_measurement", "data_chance"]


class Competency(BaseModel):
    id: str
    title: str
    description: str = ""
    area: Area
    grade_hint: int | None = None
    prerequisites: list[str] = Field(default_factory=list)
    status: Literal["draft", "reviewed"] = "draft"
    bkt: BktParams


class CompetencyGraph:
    def __init__(self, competencies: list[Competency]) -> None:
        self._by_id: dict[str, Competency] = {}
        for competency in competencies:
            if competency.id in self._by_id:
                raise ValueError(f"duplicate competency id '{competency.id}'")
            self._by_id[competency.id] = competency
        self._check_prerequisites_exist()
        self._depth = self._compute_depths()

    @classmethod
    def load(cls, path: Path) -> "CompetencyGraph":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        defaults = data.get("defaults", {}).get("bkt", {})
        competencies = [
            Competency(**{**item, "bkt": {**defaults, **item.get("bkt", {})}})
            for item in data["competencies"]
        ]
        return cls(competencies)

    def __iter__(self) -> Iterator[Competency]:
        return iter(self._by_id.values())

    def __len__(self) -> int:
        return len(self._by_id)

    def __contains__(self, competency_id: str) -> bool:
        return competency_id in self._by_id

    def get(self, competency_id: str) -> Competency:
        return self._by_id[competency_id]

    def prerequisites(self, competency_id: str) -> list[Competency]:
        return [self._by_id[p] for p in self._by_id[competency_id].prerequisites]

    def ancestors(self, competency_id: str) -> list[Competency]:
        """All competencies below this one, direct and indirect prerequisites."""
        seen: dict[str, Competency] = {}
        todo = list(self._by_id[competency_id].prerequisites)
        while todo:
            current = todo.pop()
            if current not in seen:
                seen[current] = self._by_id[current]
                todo.extend(self._by_id[current].prerequisites)
        return list(seen.values())

    def depth(self, competency_id: str) -> int:
        """Longest prerequisite chain below this competency. Roots have depth 0."""
        return self._depth[competency_id]

    def _check_prerequisites_exist(self) -> None:
        for competency in self._by_id.values():
            for prerequisite in competency.prerequisites:
                if prerequisite not in self._by_id:
                    raise ValueError(
                        f"'{competency.id}' requires unknown competency '{prerequisite}'"
                    )

    def _compute_depths(self) -> dict[str, int]:
        depths: dict[str, int] = {}
        visiting: set[str] = set()

        def depth(competency_id: str) -> int:
            if competency_id in depths:
                return depths[competency_id]
            if competency_id in visiting:
                raise ValueError(f"cycle in prerequisites at '{competency_id}'")
            visiting.add(competency_id)
            prerequisites = self._by_id[competency_id].prerequisites
            depths[competency_id] = 1 + max((depth(p) for p in prerequisites), default=-1)
            visiting.remove(competency_id)
            return depths[competency_id]

        for competency_id in self._by_id:
            depth(competency_id)
        return depths
