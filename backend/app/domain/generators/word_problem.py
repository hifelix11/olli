"""kind: word_problem. A hand-written sentence from settings.items with drawn numbers.

Each item: prompt with {a} and {b}, op ("+", "−" or "×"). The answer is computed.
Constraints: sum_max (+), result_min (−, default 0), product_max (×, default 20).
"""

import random
from collections.abc import Callable

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

OPS: dict[str, Callable[[int, int], int]] = {
    "+": lambda x, y: x + y,
    "−": lambda x, y: x - y,
    "×": lambda x, y: x * y,
}


def fits(op: str, x: int, y: int, c: dict[str, int | bool], sum_max: int) -> bool:
    if op == "+":
        return x + y <= c.get("sum_max", sum_max)
    if op == "−":
        return x - y >= c.get("result_min", 0)
    return x * y <= c.get("product_max", 20)


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    item = choose(list(s.settings["items"]), spec, level, rng)
    op = item["op"]
    a, b = s.params["a"], s.params["b"]
    pairs = [
        (x, y)
        for x in a.values()
        for y in b.values()
        if fits(op, x, y, s.constraints, a.max + b.max)
    ]
    x, y = choose(pairs, spec, level, rng)
    operands: dict[str, int | str] = {"a": x, "b": y, "op": op}
    return make_task(s, level, operands, OPS[op](x, y), item["prompt"])
