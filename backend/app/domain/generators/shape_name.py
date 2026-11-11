"""kind: shape_name. One shape is shown: what is it called?

settings.shapes: ids from shapes.CORNERS, each with a label.
settings.rotations: degrees, default [0].
Options: the shape and one shape from each of two other families.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task
from app.domain.generators.shapes import FAMILIES, family


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
    values = [shape, *(rng.choice(f) for f in rng.sample(others, 2))]
    rng.shuffle(values)
    operands: dict[str, int | str] = {"shapes": shape, "rotation": rotation}
    return make_task(s, level, operands, shape, s.template(), s.options(values))
