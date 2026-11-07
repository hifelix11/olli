"""kind: cycle_neighbour. What comes after (or before) an item of a cycle, e.g. weekdays?

settings.cycles: list of {items, after, before}; after and before are prompts with {item}.
settings.directions: subset of [after, before]. Options: the answer and two other items.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    cycle = rng.choice(s.settings["cycles"])
    direction = rng.choice(s.settings.get("directions", ["after", "before"]))
    items: list[str] = cycle["items"]
    i = rng.randrange(len(items))
    answer = items[(i + (1 if direction == "after" else -1)) % len(items)]
    others = [x for x in items if x not in (items[i], answer)]
    options: list[int | str] = [answer, *rng.sample(others, 2)]
    rng.shuffle(options)
    operands: dict[str, int | str] = {"item": items[i], "direction": direction}
    return make_task(s, level, operands, answer, cycle[direction], options)
