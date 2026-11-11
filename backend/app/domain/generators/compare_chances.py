"""kind: compare_chances. Two bags with the same number of marbles: where is red more likely?

Answers: A, B.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    triples = [
        (t, ra, rb)
        for t in s.params["total"].values()
        for ra in s.params["red_a"].values()
        for rb in s.params["red_b"].values()
        if ra <= t and rb <= t and ra != rb
    ]
    t, ra, rb = choose(triples, spec, level, rng)
    operands: dict[str, int | str] = {"red_a": ra, "blue_a": t - ra, "red_b": rb, "blue_b": t - rb}
    answer = "A" if ra > rb else "B"
    return make_task(s, level, operands, answer, s.template(), s.options(["A", "B"]))
