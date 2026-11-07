"""kind: item_choice. One hand-written question from settings.items, answered by choice.

Each item: prompt (may use {a}, {b} from params), answer, options (default: settings.options).
The content is the spec. The generator draws an item and fills the params.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    item = choose(list(s.settings["items"]), spec, level, rng)
    options: list[int | str] = list(item.get("options", s.settings.get("options", [])))
    if item["answer"] not in options:
        raise ValueError(f"generator '{spec.id}': answer '{item['answer']}' is not an option")
    operands: dict[str, int | str] = {k: rng.choice(list(r.values())) for k, r in s.params.items()}
    return make_task(s, level, operands, item["answer"], item["prompt"], options)
