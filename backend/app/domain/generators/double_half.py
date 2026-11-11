"""kind: double_half. Double n, or halve 2n. prompts: double, half."""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    n = choose(list(s.params["n"].values()), spec, level, rng)
    mode = rng.choice(["double", "half"])
    value, answer = (n, 2 * n) if mode == "double" else (2 * n, n)
    return make_task(s, level, {"value": value, "mode": mode}, answer, s.template(mode))
