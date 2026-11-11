"""kind: addition. a + b = ? Constraints: sum_min, sum_max, no_carry, carry."""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    a, b, c = s.params["a"], s.params["b"], s.constraints
    sum_min = c.get("sum_min", 0)
    sum_max = c.get("sum_max", a.max + b.max)
    pairs = [
        (x, y)
        for x in a.values()
        for y in b.values()
        if sum_min <= x + y <= sum_max
        and (not c.get("no_carry") or x % 10 + y % 10 <= 9)
        and (not c.get("carry") or x % 10 + y % 10 >= 10)
    ]
    x, y = choose(pairs, spec, level, rng)
    return make_task(s, level, {"a": x, "b": y}, x + y, s.template())
