"""kind: money_exchange. Change an amount into pieces of one value: how many pieces?

settings.pieces: list of {value, name}, e.g. {value: 2, name: Münzen}. Constraint: amount_max (20).
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

PROMPT = "Du wechselst {amount} € in lauter {value}-€-{name}. Wie viele {name} bekommst du?"


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
        "name": piece["name"],
    }
    return make_task(s, level, operands, amount // piece["value"], PROMPT)
