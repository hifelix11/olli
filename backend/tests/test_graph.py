import pytest

from app.domain.graph.graph import BktParams, Competency, CompetencyGraph

BKT = BktParams(p_init=0.2, p_learn=0.15, p_slip=0.1, p_guess=0.05)


def competency(id: str, *prerequisites: str) -> Competency:
    return Competency(
        id=id, title=id, area="numbers_operations", prerequisites=list(prerequisites), bkt=BKT
    )


def test_loads_content_graph(graph: CompetencyGraph) -> None:
    assert len(graph) == 68
    goal = graph.get("add_within_20_with_carry")
    assert [p.id for p in graph.prerequisites(goal.id)] == [
        "complement_to_10",
        "number_decomposition_to_10",
        "add_ten_plus",
    ]
    assert goal.bkt.p_guess == 0.05  # from defaults


def test_depth_is_longest_prerequisite_chain(graph: CompetencyGraph) -> None:
    assert graph.depth("number_sequence_to_10") == 0
    assert graph.depth("count_to_20") == 2
    assert graph.depth("number_decomposition_to_10") == 3
    assert graph.depth("complement_to_10") == 4
    assert graph.depth("add_within_20_with_carry") == 6


def test_rejects_unknown_prerequisite() -> None:
    with pytest.raises(ValueError, match="unknown competency 'b'"):
        CompetencyGraph([competency("a", "b")])


def test_rejects_cycle() -> None:
    with pytest.raises(ValueError, match="cycle"):
        CompetencyGraph([competency("a", "b"), competency("b", "a")])


def test_rejects_duplicate_id() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        CompetencyGraph([competency("a"), competency("a")])
