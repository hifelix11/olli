"""kind: compare_lengths. Two bars A and B: which is longer (or shorter)?

params: a, b (lengths in squares). settings.ask: subset of [longer, shorter].
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

PROMPTS = {"longer": "Welcher Stab ist länger?", "shorter": "Welcher Stab ist kürzer?"}
OPTIONS: list[int | str] = ["A", "B", "gleich lang"]


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    pairs = [(x, y) for x in s.params["a"].values() for y in s.params["b"].values()]
    x, y = choose(pairs, spec, level, rng)
    ask = rng.choice(s.settings.get("ask", ["longer"]))
    if x == y:
        answer = "gleich lang"
    else:
        answer = "A" if (x > y) == (ask == "longer") else "B"
    operands: dict[str, int | str] = {"a": x, "b": y, "ask": ask}
    return make_task(s, level, operands, answer, PROMPTS[ask], OPTIONS)
