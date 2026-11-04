"""kind: count. Show n objects, ask how many. The representation decides how they look."""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

PROMPT = "Wie viele sind es?"


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    n = choose(list(s.params["n"].values()), spec, level, rng)
    return make_task(s, level, {"n": n}, n, PROMPT)
