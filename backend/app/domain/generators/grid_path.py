"""kind: grid_path. Follow legs like "2 nach rechts und 1 nach oben" from the start.

settings: width, height. params: legs (number of legs), steps (per leg).
labels right, left, up and down name one leg with {n} steps; label "and" joins the last leg.
The prompt shows the legs as {route}. Three cells carry letters: the goal and two cells
reached by mixing up a direction. Answers: A, B, C.
"""

import random

from app.domain.generators.figures import Cell
from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

DIRECTIONS: dict[str, Cell] = {"right": (1, 0), "left": (-1, 0), "up": (0, -1), "down": (0, 1)}
MIRROR = {"right": "left", "left": "right", "up": "down", "down": "up"}
LETTERS = ["A", "B", "C"]

Leg = tuple[str, int]


def walk(start: Cell, legs: list[Leg]) -> Cell:
    x, y = start
    for direction, steps in legs:
        dx, dy = DIRECTIONS[direction]
        x, y = x + dx * steps, y + dy * steps
    return (x, y)


def describe(spec: GeneratorSpec, legs: list[Leg]) -> str:
    parts = [spec.label(direction, n=steps) for direction, steps in legs]
    if len(parts) == 1:
        return parts[0]
    return f"{', '.join(parts[:-1])} {spec.label('and')} {parts[-1]}"


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
        "legs": " ".join(f"{direction}:{steps}" for direction, steps in legs),
        "end": f"{goal[0]},{goal[1]}",
    }
    answer = LETTERS[cells.index(goal)]
    words = {"route": describe(s, legs)}
    return make_task(s, level, operands, answer, s.template(), s.options(LETTERS), words)
