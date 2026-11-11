"""Plane shapes shared by the shape kinds: ids, corner counts, families.

The names are labels in the specs.

A family groups shapes whose names overlap (a square is also a rectangle and a quadrilateral).
Distractors never come from the answer's family, so every choice task has one right option.
"""

CORNERS = {
    "triangle": 3,
    "circle": 0,
    "square": 4,
    "rectangle": 4,
    "quadrilateral": 4,
    "pentagon": 5,
    "hexagon": 6,
}
FAMILIES = [
    ["triangle"],
    ["circle"],
    ["square", "rectangle", "quadrilateral"],
    ["pentagon"],
    ["hexagon"],
]


def family(shape: str) -> list[str]:
    return next(f for f in FAMILIES if shape in f)
