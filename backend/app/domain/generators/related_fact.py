"""kind: related_fact. Show a known fact, ask the related one.

settings.relation: commutative (b + a), inverse (c − b), neighbour (a + a → a + (a + 1)).
Constraint: sum_max.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

PROMPTS = {
    "commutative": "{a} + {b} = {c}. Also: {b} + {a} = _",
    "inverse": "{a} + {b} = {c}. Also: {c} − {b} = _",
    "neighbour": "{a} + {a} = {c}. Also: {a} + {d} = _",
}


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    relation = s.settings["relation"]
    a, b = s.params["a"], s.params["b"]
    sum_max = s.constraints.get("sum_max", a.max + b.max)
    if relation == "neighbour":
        pairs = [(x, x) for x in a.values() if 2 * x + 1 <= sum_max]
    else:
        pairs = [(x, y) for x in a.values() for y in b.values() if x != y and x + y <= sum_max]
    x, y = choose(pairs, spec, level, rng)
    operands: dict[str, int | str] = {"a": x, "b": y, "c": x + y, "d": x + 1}
    answer = {"commutative": x + y, "inverse": x, "neighbour": 2 * x + 1}[relation]
    return make_task(s, level, operands, answer, PROMPTS[relation])
