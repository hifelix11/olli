"""kind: missing_addend. Task a + ? = target with a < target."""

import random

from app.domain.generators.models import GeneratorSpec, Task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.at_level(level)
    a, target = s.params["a"], s.params["target"]
    pairs = [
        (x, t) for x in range(a.min, a.max + 1) for t in range(target.min, target.max + 1) if x < t
    ]
    if not pairs:
        raise ValueError(f"generator '{spec.id}' has no valid tasks at level '{level}'")
    x, t = rng.choice(pairs)
    return Task(
        competency=spec.competency,
        generator=spec.id,
        kind="missing_addend",
        level=level,
        operands={"a": x, "target": t},
        answer=t - x,
        answer_type=spec.answer,
        representations=spec.representations,
    )
