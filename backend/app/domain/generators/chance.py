"""kind: chance. A bag of red and blue marbles: is drawing a colour certain, possible or not?

Answers: certain, possible, impossible. The prompt names the asked colour as {color}.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    pairs = [
        (r, b) for r in s.params["red"].values() for b in s.params["blue"].values() if r + b >= 1
    ]
    red, blue = choose(pairs, spec, level, rng)
    ask = rng.choice(["red", "blue"])
    count = red if ask == "red" else blue
    answer = "certain" if count == red + blue else "impossible" if count == 0 else "possible"
    operands: dict[str, int | str] = {"red": red, "blue": blue, "ask": ask}
    options = s.options(["certain", "possible", "impossible"])
    words = {"color": s.label(ask)}
    return make_task(s, level, operands, answer, s.template(), options, words)
