"""kind: even_odd. Is n even or odd? Answers: even, odd."""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    n = choose(list(s.params["n"].values()), spec, level, rng)
    answer = "even" if n % 2 == 0 else "odd"
    options = s.options(["even", "odd"])
    return make_task(s, level, {"n": n}, answer, s.template(), options)
