"""Paths to the content folders at the repo root, and the loaded content."""

from functools import cache
from pathlib import Path

from app.domain.generators.generate import load_specs
from app.domain.generators.models import GeneratorSpec
from app.domain.graph.graph import CompetencyGraph

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "content"


@cache
def load_graph() -> CompetencyGraph:
    return CompetencyGraph.load(CONTENT_DIR / "math" / "competencies.yaml")


@cache
def load_generators() -> dict[str, GeneratorSpec]:
    return load_specs(CONTENT_DIR / "math" / "generators", load_graph())
