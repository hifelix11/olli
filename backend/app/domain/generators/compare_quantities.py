"""kind: compare_quantities. Two quantities with a unit: which is more (or less)?

params: a, b. settings: unit, more and less (the prompts), ask (subset of [more, less]).
Options are the two quantities with their unit.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    unit = s.settings["unit"]
    pairs = [(x, y) for x in s.params["a"].values() for y in s.params["b"].values() if x != y]
    x, y = choose(pairs, spec, level, rng)
    ask = rng.choice(s.settings.get("ask", ["more"]))
    winner = max(x, y) if ask == "more" else min(x, y)
    options: list[int | str] = [f"{x} {unit}", f"{y} {unit}"]
    operands: dict[str, int | str] = {"a": x, "b": y, "unit": unit, "ask": ask}
    return make_task(s, level, operands, f"{winner} {unit}", s.settings[ask], options)
