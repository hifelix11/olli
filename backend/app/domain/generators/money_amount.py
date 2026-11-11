"""kind: money_amount. Coins and notes are shown: how much is it?

params: count (number of pieces). settings: values (list), unit ("€" or "ct").
Constraint: total_max. The pieces come sorted, largest first.
"""

import random
from itertools import combinations_with_replacement

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    values = sorted(s.settings["values"], reverse=True)
    total_max = s.constraints.get("total_max", 20)
    count = choose(list(s.params["count"].values()), spec, level, rng)
    sets = [c for c in combinations_with_replacement(values, count) if sum(c) <= total_max]
    coins = choose(sets, spec, level, rng)
    operands: dict[str, int | str] = {
        "coins": " ".join(str(v) for v in coins),
        "unit": s.settings.get("unit", "€"),
    }
    return make_task(s, level, operands, sum(coins), s.template())
