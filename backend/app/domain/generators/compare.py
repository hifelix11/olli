"""kind: compare. Choose <, > or = between a and b."""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    pairs = [(x, y) for x in s.params["a"].values() for y in s.params["b"].values()]
    x, y = choose(pairs, spec, level, rng)
    answer = "<" if x < y else ">" if x > y else "="
    options = s.options(["<", ">", "="])
    return make_task(s, level, {"a": x, "b": y}, answer, s.template(), options)
