"""kind: addition. Task a + b = ? with a, b in ranges and the sum within constraints."""

import random

from app.domain.generators.models import GeneratorSpec, Task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.at_level(level)
    a, b = s.params["a"], s.params["b"]
    sum_min = s.constraints.get("sum_min", 0)
    sum_max = s.constraints.get("sum_max", a.max + b.max)
    pairs = [
        (x, y)
        for x in range(a.min, a.max + 1)
        for y in range(b.min, b.max + 1)
        if sum_min <= x + y <= sum_max
    ]
    if not pairs:
        raise ValueError(f"generator '{spec.id}' has no valid tasks at level '{level}'")
    x, y = rng.choice(pairs)
    return Task(
        competency=spec.competency,
        generator=spec.id,
        kind="addition",
        level=level,
        operands={"a": x, "b": y},
        answer=x + y,
        answer_type=spec.answer,
        representations=spec.representations,
    )
