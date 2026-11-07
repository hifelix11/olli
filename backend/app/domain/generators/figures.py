"""Pixel figures on a grid, shared by the grid kinds. A cell is (x, y), y grows downwards."""

import random

Cell = tuple[int, int]
NEIGHBOURS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def random_figure(width: int, height: int, size: int, rng: random.Random) -> set[Cell]:
    """A connected figure of `size` cells, grown from a random cell."""
    x, y = rng.randrange(width), rng.randrange(height)
    figure = {(x, y)}
    while len(figure) < size:
        x, y = rng.choice(sorted(figure))
        dx, dy = rng.choice(NEIGHBOURS)
        if 0 <= x + dx < width and 0 <= y + dy < height:
            figure.add((x + dx, y + dy))
    return figure


def border(figure: set[Cell], width: int, height: int) -> list[Cell]:
    """Empty cells next to the figure."""
    around = {
        (x + dx, y + dy)
        for x, y in figure
        for dx, dy in NEIGHBOURS
        if 0 <= x + dx < width and 0 <= y + dy < height
    }
    return sorted(around - figure)


def normalized(figure: set[Cell]) -> frozenset[Cell]:
    """The figure moved to the top left corner, to compare shapes regardless of position."""
    min_x = min(x for x, _ in figure)
    min_y = min(y for _, y in figure)
    return frozenset((x - min_x, y - min_y) for x, y in figure)


def encode(figure: set[Cell]) -> str:
    return " ".join(f"{x},{y}" for x, y in sorted(figure))
