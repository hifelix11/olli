"""kind: symmetry. A figure on a grid with a vertical axis in the middle: is it symmetric?

settings: width (even), height. params: cells (figure cells in the left half). Answers: yes, no.
Half of the tasks mirror the left half exactly, the other half flip one cell on the right.
"""

import random

from app.domain.generators.figures import encode, random_figure
from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    width, height = s.settings["width"], s.settings["height"]
    size = choose(list(s.params["cells"].values()), spec, level, rng)
    left = random_figure(width // 2, height, size, rng)
    figure = left | {(width - 1 - x, y) for x, y in left}
    symmetric = rng.random() < 0.5
    if not symmetric:
        x, y = rng.randrange(width // 2, width), rng.randrange(height)
        figure ^= {(x, y)}
    operands: dict[str, int | str] = {
        "width": width,
        "height": height,
        "cells": encode(figure),
        "axis": "vertical",
    }
    answer = "yes" if symmetric else "no"
    return make_task(s, level, operands, answer, s.template(), s.options(["yes", "no"]))
