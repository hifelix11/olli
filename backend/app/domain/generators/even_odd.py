"""kind: even_odd. Is n even or odd?"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

OPTIONS: list[int | str] = ["gerade", "ungerade"]
PROMPT = "Ist {n} gerade oder ungerade?"


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    n = choose(list(s.params["n"].values()), spec, level, rng)
    answer = "gerade" if n % 2 == 0 else "ungerade"
    return make_task(s, level, {"n": n}, answer, PROMPT, OPTIONS)
