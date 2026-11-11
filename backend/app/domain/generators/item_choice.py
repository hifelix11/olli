"""kind: item_choice. One hand-written question from settings.items, answered by choice.

Each item: prompt (may use {a}, {b} from params), answer, options (default: settings.options).
Options are values: IDs take their label from the spec's labels. An item may also give
its options as a map from ID to label, for texts that only this item uses.
The content is the spec. The generator draws an item and fills the params.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    item = choose(list(s.settings["items"]), spec, level, rng)
    values = item.get("options", s.settings.get("options", []))
    if isinstance(values, dict):
        s = s.model_copy(update={"labels": {**s.labels, **values}})
    if item["answer"] not in values:
        raise ValueError(f"generator '{spec.id}': answer '{item['answer']}' is not an option")
    operands: dict[str, int | str] = {k: rng.choice(list(r.values())) for k, r in s.params.items()}
    return make_task(s, level, operands, item["answer"], item["prompt"], s.options(values))
