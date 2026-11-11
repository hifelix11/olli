"""kind: measure. A bar is shown against units or a ruler: how long is it?

params: n. label unit: the unit's name, e.g. Büroklammern or Zentimeter, as {unit}.
The representation (units, ruler) decides what the child sees.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    n = choose(list(s.params["n"].values()), spec, level, rng)
    return make_task(s, level, {"n": n, "unit": s.label("unit")}, n, s.template())
