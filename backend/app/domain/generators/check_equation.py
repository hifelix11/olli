"""kind: check_equation. Is the shown result right or wrong?

settings.operations: subset of ["+", "−"]. Constraints: sum_max (for +), result_min (for −).
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

OPTIONS: list[int | str] = ["richtig", "falsch"]
PROMPT = "Stimmt das? {a} {op} {b} = {result}"


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    a, b, c = s.params["a"], s.params["b"], s.constraints
    op = rng.choice(s.settings.get("operations", ["+"]))
    if op == "+":
        sum_max = c.get("sum_max", a.max + b.max)
        pairs = [(x, y) for x in a.values() for y in b.values() if x + y <= sum_max]
    else:
        result_min = c.get("result_min", 0)
        pairs = [(x, y) for x in a.values() for y in b.values() if x - y >= result_min]
    x, y = choose(pairs, spec, level, rng)
    true_result = x + y if op == "+" else x - y
    correct = rng.random() < 0.5
    shown = true_result
    if not correct:
        shown = true_result + rng.choice([-2, -1, 1, 2])
        if shown < 0:
            shown = true_result + 1
    operands: dict[str, int | str] = {"a": x, "b": y, "op": op, "result": shown}
    return make_task(s, level, operands, "richtig" if correct else "falsch", PROMPT, OPTIONS)
