"""kind: missing_number. One number of a + b = c is hidden. settings.forms picks the shape.

prompts: one per form, e.g. "a+_=c": "{a} + _ = {c}".
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

HIDDEN = {"a+_=c": "b", "_+b=c": "a", "c-_=a": "b", "_-b=a": "c"}


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    a, target = s.params["a"], s.params["target"]
    triples = [(x, t - x, t) for x in a.values() for t in target.values() if x < t]
    x, y, t = choose(triples, spec, level, rng)
    form = rng.choice(s.settings.get("forms", ["a+_=c"]))
    operands: dict[str, int | str] = {"a": x, "b": y, "c": t, "form": form}
    return make_task(s, level, operands, operands[HIDDEN[form]], s.template(form))
