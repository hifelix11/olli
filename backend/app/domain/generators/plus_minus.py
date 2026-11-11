"""kind: plus_minus. Addition or subtraction, drawn per task.

settings.operations: subset of ["+", "−"]. Constraints as for addition and subtraction.
prompts: one per operation, "+" and "−".
"""

import random

from app.domain.generators import addition, subtraction
from app.domain.generators.models import GeneratorSpec, Task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    op = rng.choice(s.settings.get("operations", ["+", "−"]))
    # Resolved once here; the delegate must not apply variants or levels a second time.
    s = s.model_copy(update={"variants": [], "levels": {}, "prompt": s.template(op)})
    task = (addition if op == "+" else subtraction).generate(s, level, rng)
    return task.model_copy(update={"operands": {**task.operands, "op": op}})
