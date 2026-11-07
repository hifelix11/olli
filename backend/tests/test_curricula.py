"""Every curriculum mapping points at real competencies, and every competency is mapped."""

from app.content import CURRICULA_DIR
from app.domain.curriculum import Curriculum
from app.domain.graph.graph import CompetencyGraph


def test_bavaria_grade_1_mapping_is_consistent(graph: CompetencyGraph) -> None:
    curriculum = Curriculum.load(CURRICULA_DIR / "de-by" / "math-1.yaml")
    assert (curriculum.state, curriculum.grade) == ("de-by", 1)
    unknown = curriculum.competencies - {c.id for c in graph}
    unmapped = {c.id for c in graph} - curriculum.competencies
    assert not unknown, f"mapping names unknown competencies: {sorted(unknown)}"
    assert not unmapped, f"competencies without curriculum reference: {sorted(unmapped)}"
