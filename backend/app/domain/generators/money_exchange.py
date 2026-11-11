"""kind: money_exchange. Change an amount into pieces of one value: how many pieces?

settings.pieces: list of {value, type}, e.g. {value: 2, type: coins}. The type's label is {name}.
Constraint: amount_max (20).
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    amount_max = s.constraints.get("amount_max", 20)
    candidates = [
        (piece, amount)
        for piece in s.settings["pieces"]
        for amount in range(2 * piece["value"], amount_max + 1, piece["value"])
    ]
    piece, amount = choose(candidates, spec, level, rng)
    operands: dict[str, int | str] = {
        "amount": amount,
        "value": piece["value"],
        "type": piece["type"],
    }
    words = {"name": s.label(piece["type"])}
    return make_task(s, level, operands, amount // piece["value"], s.template(), words=words)
