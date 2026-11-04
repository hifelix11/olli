"""kind: chance. A bag of red and blue marbles: is drawing a colour certain, possible or not?"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

OPTIONS: list[int | str] = ["sicher", "möglich", "unmöglich"]
PROMPT = (
    "Im Säckchen sind {red} rote und {blue} blaue Kugeln. Du ziehst eine Kugel. "
    "Ist es sicher, möglich oder unmöglich, dass sie {ask} ist?"
)


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    pairs = [
        (r, b) for r in s.params["red"].values() for b in s.params["blue"].values() if r + b >= 1
    ]
    red, blue = choose(pairs, spec, level, rng)
    ask = rng.choice(["rot", "blau"])
    count = red if ask == "rot" else blue
    answer = "sicher" if count == red + blue else "unmöglich" if count == 0 else "möglich"
    operands: dict[str, int | str] = {"red": red, "blue": blue, "ask": ask}
    return make_task(s, level, operands, answer, PROMPT, OPTIONS)
