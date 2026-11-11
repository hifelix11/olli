import random
import re
from collections.abc import Iterable
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StrictInt, StrictStr

# Values the code compares and stores are IDs like "even".
# A child never sees an ID: every ID needs a label.
ID = re.compile(r"[a-z][a-z0-9_]*")


class Plural(BaseModel):
    """A text with a singular and a plural form, chosen by the count n."""

    model_config = ConfigDict(extra="forbid")
    one: str
    other: str


Text = str | Plural
# Strict: YAML reads yes and no as true and false. A value must never turn into 1 or 0.
Value = StrictInt | StrictStr


def _string_keys(labels: dict[Any, Any]) -> dict[str, Any]:
    """YAML reads keys like 5 as numbers. Labels are looked up by string."""
    if any(isinstance(k, bool) for k in labels):
        raise ValueError('label keys yes and no need quotes: "yes", "no"')
    return {str(k): v for k, v in labels.items()}


Labels = Annotated[dict[str, Text], BeforeValidator(_string_keys)]


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
    prompts: dict[str, str] = Field(default_factory=dict)
    labels: Labels = Field(default_factory=dict)


class Option(BaseModel):
    """A choice. The value is compared and stored, the label is shown."""

    value: Value
    label: str


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
    prompts: dict[str, str] = Field(default_factory=dict)  # one prompt per form
    labels: Labels = Field(default_factory=dict)  # texts for IDs, may use placeholders
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
                "prompts": {**self.prompts, **override.prompts},
                "labels": {**self.labels, **override.labels},
            }
        )

    def template(self, form: str | None = None) -> str:
        """The prompt, or the prompt of one form."""
        text = self.prompt if form is None else self.prompts.get(form)
        if text is None:
            raise ValueError(
                f"generator '{self.id}' has no prompt" + (f" '{form}'" if form else "")
            )
        return text

    def label(self, key: int | str, n: int | None = None, **fields: int | str) -> str:
        """The text for an ID. n picks the plural form and fills {n}."""
        text = self.labels.get(str(key))
        if text is None:
            raise ValueError(f"generator '{self.id}' has no label '{key}'")
        if isinstance(text, Plural):
            text = text.one if n == 1 else text.other
        return text.format(n=n, **fields)

    def options(self, values: Iterable[int | str]) -> list[Option]:
        """IDs show their label. Numbers, letters and signs like "<" show as they are."""
        return [
            Option(value=v, label=self.label(v) if self._labelled(v) else str(v)) for v in values
        ]

    def _labelled(self, value: int | str) -> bool:
        return str(value) in self.labels or (isinstance(value, str) and bool(ID.fullmatch(value)))


class Task(BaseModel):
    competency: str
    generator: str
    kind: str
    level: str
    prompt: str
    operands: dict[str, int | str]
    answer: Value  # never a label
    options: list[Option] | None = None  # present for choice tasks
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
    prompt: str,
    options: list[Option] | None = None,
    words: dict[str, str] | None = None,
) -> Task:
    """The prompt is a template. It sees the operands and the words, texts made only for it."""
    return Task(
        competency=spec.competency,
        generator=spec.id,
        kind=spec.kind,
        level=level,
        prompt=prompt.format(**operands, **(words or {})),
        operands=operands,
        answer=answer,
        options=options,
        representations=spec.representations,
    )
