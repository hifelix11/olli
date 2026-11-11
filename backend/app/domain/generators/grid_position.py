"""kind: grid_position. Letters around the Käfer: which one is left, right, above or below it?

settings: width, height, relations (subset of RELATIONS keys). Three letters sit next to the Käfer.
Each relation has a label, shown in the prompt as {place}. Answers: A, B, C.
"""

import random

from app.domain.generators.figures import Cell
from app.domain.generators.models import GeneratorSpec, Task, make_task

RELATIONS: dict[str, Cell] = {"left": (-1, 0), "right": (1, 0), "above": (0, -1), "below": (0, 1)}
LETTERS = ["A", "B", "C"]


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    width, height = s.settings["width"], s.settings["height"]
    relations = list(s.settings.get("relations", RELATIONS))
    # The Käfer stays away from the edge, so every neighbour cell is on the grid.
    x, y = rng.randrange(1, width - 1), rng.randrange(1, height - 1)
    asked = rng.choice(relations)
    others = [r for r in RELATIONS if r != asked]
    placed = [asked, *rng.sample(others, 2)]
    rng.shuffle(placed)
    marks = []
    for letter, relation in zip(LETTERS, placed, strict=True):
        dx, dy = RELATIONS[relation]
        marks.append(f"{letter}:{x + dx},{y + dy}")
    answer = LETTERS[placed.index(asked)]
    operands: dict[str, int | str] = {
        "width": width,
        "height": height,
        "start": f"{x},{y}",
        "marks": " ".join(marks),
        "relation": asked,
    }
    words = {"place": s.label(asked)}
    return make_task(s, level, operands, answer, s.template(), s.options(LETTERS), words)
