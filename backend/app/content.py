"""Paths to the content folders at the repo root, and the loaded content."""

from functools import cache
from pathlib import Path

from app.domain.curriculum import Curriculum
from app.domain.generators.generate import load_specs
from app.domain.generators.models import GeneratorSpec
from app.domain.graph.graph import CompetencyGraph

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "content"
CURRICULA_DIR = REPO_ROOT / "curricula"


@cache
def load_graph() -> CompetencyGraph:
    return CompetencyGraph.load(CONTENT_DIR / "math" / "competencies.yaml")


@cache
def load_generators() -> dict[str, GeneratorSpec]:
    return load_specs(CONTENT_DIR / "math" / "generators", load_graph())


@cache
def load_curriculum() -> Curriculum:
    """Bavaria, grade 1, until children carry their own state and grade."""
    return Curriculum.load(CURRICULA_DIR / "de-by" / "math-1.yaml")
