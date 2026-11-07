"""kind: picture_equation. Counters come in or go away: which equation fits?

settings.operations: subset of ["+", "−"]. Constraints: sum_max (+), result_min (−).
The spec's prompt may wrap the numbers in a scene: "Im Korb sind {a} Äpfel. {b} {action}."
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

ACTIONS = {"+": ("kommt dazu", "kommen dazu"), "−": ("wird weggenommen", "werden weggenommen")}
PROMPT = "{a} Plättchen. {b} {action}. Welche Aufgabe passt?"


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
    options: list[int | str] = [f"{x} + {y}", f"{x} − {y}", f"{y} − {x}"]
    rng.shuffle(options)
    singular, plural = ACTIONS[op]
    operands: dict[str, int | str] = {
        "a": x,
        "b": y,
        "op": op,
        "action": singular if y == 1 else plural,
    }
    return make_task(s, level, operands, f"{x} {op} {y}", PROMPT, options)
