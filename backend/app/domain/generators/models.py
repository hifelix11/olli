from typing import Literal

from pydantic import BaseModel, Field


class Range(BaseModel):
    min: int
    max: int


class Level(BaseModel):
    params: dict[str, Range] = Field(default_factory=dict)
    constraints: dict[str, int] = Field(default_factory=dict)


class GeneratorSpec(BaseModel):
    id: str
    competency: str
    kind: str
    params: dict[str, Range]
    constraints: dict[str, int] = Field(default_factory=dict)
    levels: dict[str, Level] = Field(default_factory=dict)
    answer: Literal["free_input", "choice"] = "free_input"
    representations: list[str] = Field(default_factory=lambda: ["plain"])

    def at_level(self, level: str) -> "GeneratorSpec":
        """Copy of this spec with the level's overrides applied. Unknown levels change nothing."""
        override = self.levels.get(level, Level())
        return self.model_copy(
            update={
                "params": {**self.params, **override.params},
                "constraints": {**self.constraints, **override.constraints},
            }
        )


class Task(BaseModel):
    competency: str
    generator: str
    kind: str
    level: str
    operands: dict[str, int]
    answer: int
    answer_type: Literal["free_input", "choice"]
    representations: list[str]
