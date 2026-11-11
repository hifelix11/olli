"""kind: number_word. Number word in, digits out. labels: the number words, keyed by number."""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    n = choose(list(s.params["n"].values()), spec, level, rng)
    return make_task(s, level, {"n": n}, n, s.template(), words={"word": s.label(n)})
