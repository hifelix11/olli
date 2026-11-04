"""Every curriculum mapping points at real competencies, and every competency is mapped."""

import yaml

from app.content import REPO_ROOT
from app.domain.graph.graph import CompetencyGraph

CURRICULA_DIR = REPO_ROOT / "curricula"


def mapped_ids(path) -> set[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {
        c for unit in data["units"] for bullet in unit["bullets"] for c in bullet["competencies"]
    }


def test_bavaria_grade_1_mapping_is_consistent(graph: CompetencyGraph) -> None:
    mapped = mapped_ids(CURRICULA_DIR / "de-by" / "math-1.yaml")
    unknown = mapped - {c.id for c in graph}
    unmapped = {c.id for c in graph} - mapped
    assert not unknown, f"mapping names unknown competencies: {sorted(unknown)}"
    assert not unmapped, f"competencies without curriculum reference: {sorted(unmapped)}"
