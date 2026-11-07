"""kind: pattern_gap. A row of shapes repeats a unit; one shape is missing.

settings.symbols: shape ids. params: unit (length of the repeated part), repeats.
settings.gap: "end" (default) or "any". Options: the names of all symbols.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task
from app.domain.generators.shapes import NAMES

PROMPT = "Wie geht das Muster weiter?"


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    symbols: list[str] = s.settings["symbols"]
    unit_length = choose(list(s.params["unit"].values()), spec, level, rng)
    repeats = choose(list(s.params["repeats"].values()), spec, level, rng)
    unit = [rng.choice(symbols) for _ in range(unit_length)]
    while len(set(unit)) < 2:
        unit = [rng.choice(symbols) for _ in range(unit_length)]
    row = unit * repeats
    gap = len(row) - 1 if s.settings.get("gap", "end") == "end" else rng.randrange(len(row))
    shown = " ".join("_" if i == gap else x for i, x in enumerate(row))
    options: list[int | str] = [NAMES[x] for x in symbols]
    return make_task(s, level, {"shapes": shown}, NAMES[row[gap]], PROMPT, options)
