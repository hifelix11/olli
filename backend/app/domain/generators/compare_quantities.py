"""kind: compare_quantities. Two quantities with a unit: which is more (or less)?

params: a, b. settings.ask: subset of [more, less]. prompts: more, less.
label quantity shows a value with its unit, e.g. "{n} €". Answers are the values.
"""

import random

from app.domain.generators.models import GeneratorSpec, Option, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    pairs = [(x, y) for x in s.params["a"].values() for y in s.params["b"].values() if x != y]
    x, y = choose(pairs, spec, level, rng)
    ask = rng.choice(s.settings.get("ask", ["more"]))
    winner = max(x, y) if ask == "more" else min(x, y)
    options = [Option(value=v, label=s.label("quantity", n=v)) for v in (x, y)]
    operands: dict[str, int | str] = {"a": x, "b": y, "ask": ask}
    return make_task(s, level, operands, winner, s.template(ask), options)
