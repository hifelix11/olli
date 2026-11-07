"""kind: measure. A bar is shown against units or a ruler: how long is it?

params: n. settings.unit: the unit's name in the question, e.g. Büroklammern or Zentimeter.
The representation (units, ruler) decides what the child sees.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

PROMPT = "Wie viele {unit} lang ist der Stab?"


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    n = choose(list(s.params["n"].values()), spec, level, rng)
    return make_task(s, level, {"n": n, "unit": s.settings["unit"]}, n, PROMPT)
