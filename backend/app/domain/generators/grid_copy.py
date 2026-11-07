"""kind: grid_copy. A figure and its copy on two grids: is the copy right?

settings: width, height. params: cells (size of the figure).
A wrong copy has one cell moved, so that the shape differs even when shifted.
"""

import random

from app.domain.generators.figures import border, encode, normalized, random_figure
from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

OPTIONS: list[int | str] = ["ja", "nein"]
PROMPT = "Links ist die Vorlage, rechts die Kopie. Ist die Kopie richtig?"


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    width, height = s.settings["width"], s.settings["height"]
    size = choose(list(s.params["cells"].values()), spec, level, rng)
    figure = random_figure(width, height, size, rng)
    correct = rng.random() < 0.5
    copy = figure
    while not correct and normalized(copy) == normalized(figure):
        removed = rng.choice(sorted(figure))
        copy = (figure - {removed}) | {rng.choice(border(figure, width, height))}
    operands: dict[str, int | str] = {
        "width": width,
        "height": height,
        "cells": encode(figure),
        "copy": encode(copy),
    }
    return make_task(s, level, operands, "ja" if correct else "nein", PROMPT, OPTIONS)
