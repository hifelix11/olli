import random
from typing import Any, Literal

from pydantic import BaseModel, Field


class Range(BaseModel):
    min: int
    max: int

    def values(self) -> range:
        return range(self.min, self.max + 1)


class Override(BaseModel):
    """Partial spec applied on top of the base: used for variants and levels."""

    params: dict[str, Range] = Field(default_factory=dict)
    constraints: dict[str, int | bool] = Field(default_factory=dict)
    settings: dict[str, Any] = Field(default_factory=dict)


class GeneratorSpec(BaseModel):
    id: str
    competency: str
    kind: str
    params: dict[str, Range] = Field(default_factory=dict)
    constraints: dict[str, int | bool] = Field(default_factory=dict)
    settings: dict[str, Any] = Field(default_factory=dict)
    variants: list[Override] = Field(default_factory=list)
    levels: dict[str, Override] = Field(default_factory=dict)
    prompt: str | None = None
    answer: Literal["free_input", "choice"] = "free_input"
    representations: list[str] = Field(default_factory=lambda: ["plain"])

    def resolve(self, level: str, rng: random.Random) -> "GeneratorSpec":
        """Base, then one random variant, then the level's overrides. Unknown level: no change."""
        spec = self
        if self.variants:
            spec = spec._apply(rng.choice(self.variants))
        return spec._apply(self.levels.get(level, Override()))

    def _apply(self, override: Override) -> "GeneratorSpec":
        return self.model_copy(
            update={
                "params": {**self.params, **override.params},
                "constraints": {**self.constraints, **override.constraints},
                "settings": {**self.settings, **override.settings},
            }
        )


class Task(BaseModel):
    competency: str
    generator: str
    kind: str
    level: str
    prompt: str
    operands: dict[str, int | str]
    answer: int | str
    options: list[int | str] | None = None  # present for choice tasks
    representations: list[str]


def choose[T](candidates: list[T], spec: GeneratorSpec, level: str, rng: random.Random) -> T:
    if not candidates:
        raise ValueError(f"generator '{spec.id}' has no valid tasks at level '{level}'")
    return rng.choice(candidates)


def make_task(
    spec: GeneratorSpec,
    level: str,
    operands: dict[str, int | str],
    answer: int | str,
    default_prompt: str,
    options: list[int | str] | None = None,
) -> Task:
    return Task(
        competency=spec.competency,
        generator=spec.id,
        kind=spec.kind,
        level=level,
        prompt=(spec.prompt or default_prompt).format(**operands),
        operands=operands,
        answer=answer,
        options=options,
        representations=spec.representations,
    )
