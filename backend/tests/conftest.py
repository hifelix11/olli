import pytest

from app.content import CONTENT_DIR
from app.domain.generators.generate import load_specs
from app.domain.generators.models import GeneratorSpec
from app.domain.graph.graph import CompetencyGraph


@pytest.fixture(scope="session")
def graph() -> CompetencyGraph:
    return CompetencyGraph.load(CONTENT_DIR / "math" / "competencies.yaml")


@pytest.fixture(scope="session")
def specs(graph: CompetencyGraph) -> dict[str, GeneratorSpec]:
    return load_specs(CONTENT_DIR / "math" / "generators", graph)
