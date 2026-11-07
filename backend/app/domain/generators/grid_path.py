"""kind: grid_path. Follow legs like "2 nach rechts und 1 nach oben" from the start.

settings: width, height. params: legs (number of legs), steps (per leg).
Three cells carry letters: the goal and two cells reached by mixing up a direction.
"""

import random

from app.domain.generators.figures import Cell
from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

DIRECTIONS: dict[str, Cell] = {"rechts": (1, 0), "links": (-1, 0), "oben": (0, -1), "unten": (0, 1)}
MIRROR = {"rechts": "links", "links": "rechts", "oben": "unten", "unten": "oben"}
LETTERS: list[int | str] = ["A", "B", "C"]
PROMPT = "Der Käfer geht {legs}. Wo kommt er an?"

Leg = tuple[str, int]


def walk(start: Cell, legs: list[Leg]) -> Cell:
    x, y = start
    for direction, steps in legs:
        dx, dy = DIRECTIONS[direction]
        x, y = x + dx * steps, y + dy * steps
    return (x, y)


def describe(legs: list[Leg]) -> str:
    parts = [f"{steps} nach {direction}" for direction, steps in legs]
    return ", ".join(parts[:-1]) + (" und " if len(parts) > 1 else "") + parts[-1]


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    width, height = s.settings["width"], s.settings["height"]
    leg_count = choose(list(s.params["legs"].values()), spec, level, rng)
    step_values = list(s.params["steps"].values())

    def inside(cell: Cell) -> bool:
        return 0 <= cell[0] < width and 0 <= cell[1] < height

    while True:
        start = (rng.randrange(width), rng.randrange(height))
        legs: list[Leg] = []
        for _ in range(leg_count):
            direction = rng.choice([d for d in DIRECTIONS if not legs or d != legs[-1][0]])
            legs.append((direction, rng.choice(step_values)))
        goal = walk(start, legs)
        if inside(goal) and goal != start:
            break
    # Wrong turns: one leg mirrored. Random cells fill in when those leave the grid.
    cells = [goal]
    for i in range(len(legs)):
        mirrored = legs[:i] + [(MIRROR[legs[i][0]], legs[i][1])] + legs[i + 1 :]
        wrong = walk(start, mirrored)
        if inside(wrong) and wrong not in cells and wrong != start:
            cells.append(wrong)
    while len(cells) < 3:
        cell = (rng.randrange(width), rng.randrange(height))
        if cell not in cells and cell != start:
            cells.append(cell)
    cells = cells[:3]
    rng.shuffle(cells)
    operands: dict[str, int | str] = {
        "width": width,
        "height": height,
        "start": f"{start[0]},{start[1]}",
        "marks": " ".join(
            f"{letter}:{x},{y}" for letter, (x, y) in zip(LETTERS, cells, strict=True)
        ),
        "legs": describe(legs),
        "end": f"{goal[0]},{goal[1]}",
    }
    return make_task(s, level, operands, LETTERS[cells.index(goal)], PROMPT, LETTERS)
