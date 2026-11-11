"""kind: picture_equation. Counters come in or go away: which equation fits?

settings.operations: subset of ["+", "−"]. Constraints: sum_max (+), result_min (−).
labels add and remove name what happens to {b} counters, singular and plural: {action}.
The prompt may wrap the numbers in a scene: "Im Korb sind {a} Äpfel. {b} {action}."
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    a, b, c = s.params["a"], s.params["b"], s.constraints
    op = rng.choice(s.settings.get("operations", ["+", "−"]))
    if op == "+":
        sum_max = c.get("sum_max", a.max + b.max)
        pairs = [(x, y) for x in a.values() for y in b.values() if x != y and x + y <= sum_max]
    else:
        result_min = c.get("result_min", 0)
        pairs = [(x, y) for x in a.values() for y in b.values() if x != y and x - y >= result_min]
    x, y = choose(pairs, spec, level, rng)
    equations: list[int | str] = [f"{x} + {y}", f"{x} − {y}", f"{y} − {x}"]
    rng.shuffle(equations)
    operands: dict[str, int | str] = {"a": x, "b": y, "op": op}
    words = {"action": s.label("add" if op == "+" else "remove", n=y)}
    answer = f"{x} {op} {y}"
    return make_task(s, level, operands, answer, s.template(), s.options(equations), words)
