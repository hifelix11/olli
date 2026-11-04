"""Load generator specs from content and run the matching generator."""

import random
from collections.abc import Callable
from pathlib import Path

import yaml

from app.domain.generators import addition, missing_addend
from app.domain.generators.models import GeneratorSpec, Task
from app.domain.graph.graph import CompetencyGraph

Generator = Callable[[GeneratorSpec, str, random.Random], Task]

GENERATORS: dict[str, Generator] = {
    "addition": addition.generate,
    "missing_addend": missing_addend.generate,
}


def load_specs(directory: Path, graph: CompetencyGraph) -> dict[str, GeneratorSpec]:
    """All specs in a folder, keyed by competency. One generator per competency for now."""
    specs: dict[str, GeneratorSpec] = {}
    for path in sorted(directory.glob("*.yaml")):
        spec = GeneratorSpec(**yaml.safe_load(path.read_text(encoding="utf-8")))
        if spec.competency not in graph:
            raise ValueError(
                f"generator '{spec.id}' targets unknown competency '{spec.competency}'"
            )
        if spec.kind not in GENERATORS:
            raise ValueError(f"generator '{spec.id}' has unknown kind '{spec.kind}'")
        if spec.competency in specs:
            raise ValueError(f"competency '{spec.competency}' has more than one generator")
        specs[spec.competency] = spec
    return specs


def generate_task(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    return GENERATORS[spec.kind](spec, level, rng)
