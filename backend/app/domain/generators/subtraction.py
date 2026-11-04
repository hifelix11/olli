"""kind: subtraction. a − b = ? Constraints: result_min, result_max, no_borrow, borrow."""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

PROMPT = "{a} − {b} = ?"


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    a, b, c = s.params["a"], s.params["b"], s.constraints
    result_min = c.get("result_min", 0)
    result_max = c.get("result_max", a.max)
    pairs = [
        (x, y)
        for x in a.values()
        for y in b.values()
        if result_min <= x - y <= result_max
        and (not c.get("no_borrow") or x % 10 >= y % 10)
        and (not c.get("borrow") or x % 10 < y % 10)
    ]
    x, y = choose(pairs, spec, level, rng)
    return make_task(s, level, {"a": x, "b": y}, x - y, PROMPT)
