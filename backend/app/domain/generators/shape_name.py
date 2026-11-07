"""kind: shape_name. One shape is shown: what is it called?

settings.shapes: ids from shapes.NAMES. settings.rotations: degrees, default [0].
Options: the name and one shape from each of two other families.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task
from app.domain.generators.shapes import FAMILIES, NAMES, family

PROMPT = "Welche Form ist das?"


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    shapes: list[str] = s.settings["shapes"]
    shape = choose(shapes, spec, level, rng)
    rotation = rng.choice(s.settings.get("rotations", [0]))
    others = [
        [x for x in f if x in shapes]
        for f in FAMILIES
        if f is not family(shape) and set(f) & set(shapes)
    ]
    distractors = [rng.choice(f) for f in rng.sample(others, 2)]
    options: list[int | str] = [NAMES[shape], *(NAMES[d] for d in distractors)]
    rng.shuffle(options)
    operands: dict[str, int | str] = {"shapes": shape, "rotation": rotation}
    return make_task(s, level, operands, NAMES[shape], PROMPT, options)
