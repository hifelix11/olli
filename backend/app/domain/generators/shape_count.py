"""kind: shape_count. One shape is shown: how many corners (or sides)?

settings.shapes: ids from shapes.CORNERS. settings.ask: subset of [corners, sides].
settings.rotations: degrees, default [0]. prompts: corners, sides.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task
from app.domain.generators.shapes import CORNERS


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    shape = choose(list(s.settings["shapes"]), spec, level, rng)
    ask = rng.choice(s.settings.get("ask", ["corners"]))
    rotation = rng.choice(s.settings.get("rotations", [0]))
    operands: dict[str, int | str] = {"shapes": shape, "rotation": rotation, "ask": ask}
    return make_task(s, level, operands, CORNERS[shape], s.template(ask))
