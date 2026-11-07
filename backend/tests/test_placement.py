"""Placement check: a new learner is probed top-down before practice starts."""

import random
from collections.abc import Callable

from app.domain.generators.models import GeneratorSpec, Task
from app.domain.graph.graph import CompetencyGraph
from app.domain.selection.select import MASTERED
from app.domain.tutor import Tutor


def place(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec], knows: Callable[[str], bool]
) -> tuple[Tutor, list[Task]]:
    """Run the placement check to its end for a learner who knows exactly `knows`."""
    tutor = Tutor(graph, specs, rng=random.Random(1), placing=True)
    probes: list[Task] = []
    while True:
        task = tutor.next_task()
        if not tutor.placing:
            return tutor, probes
        assert task is not None and task.level == "medium"
        probes.append(task)
        tutor.submit(task, task.answer if knows(task.competency) else -999)


def middle(graph: CompetencyGraph, specs: dict[str, GeneratorSpec]) -> int:
    return max(graph.depth(c) for c in specs) // 2


def test_starts_in_the_middle_not_at_the_root(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    task = Tutor(graph, specs, placing=True).next_task()
    assert task is not None
    assert graph.depth(task.competency) == middle(graph, specs) > 0


def test_strong_learner_is_covered_in_few_probes(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    """Every probe covers its prerequisites, so far fewer probes than competencies are needed."""
    tutor, probes = place(graph, specs, lambda _: True)
    assert len(probes) < len(specs) // 2
    assert all(tutor.state.observed(c) for c in specs)
    assert all(tutor.state.mastery[c] > 0.4 for c in specs)
    assert len({t.competency for t in probes}) == len(probes)


def test_correct_answer_counts_for_prerequisites(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    tutor = Tutor(graph, specs, rng=random.Random(1), placing=True)
    task = tutor.next_task()
    assert task is not None
    tutor.submit(task, task.answer)
    for prerequisite in graph.ancestors(task.competency):
        assert tutor.state.observed(prerequisite.id) == (prerequisite.id in specs)
        if prerequisite.id in specs:
            assert tutor.state.mastery[prerequisite.id] > 0.8


def test_beginner_descends_to_the_root_and_stops(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    """Halve the depth after each failure, then one probe per remaining root."""
    tutor, probes = place(graph, specs, lambda _: False)
    depths = [graph.depth(t.competency) for t in probes]
    start = middle(graph, specs)
    roots = [c for c in specs if graph.depth(c) == 0]
    assert depths[:3] == [start, (start - 1) // 2, 0]
    assert len(probes) <= 2 + len(roots)
    assert all(not tutor.state.observed(c) or tutor.state.mastery[c] < 0.4 for c in specs)


def test_nothing_above_a_failure_is_probed(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    gap = "number_decomposition_to_10"
    tutor, probes = place(graph, specs, lambda c: graph.depth(c) <= 3 and c != gap)
    above = {c for c in specs if gap in {p.id for p in graph.ancestors(c)}}
    probed = [t.competency for t in probes]
    after_failure = probed[probed.index(gap) + 1 :]
    assert above and after_failure and not above & set(after_failure)
    assert tutor.state.mastery[gap] < 0.4
    assert tutor.state.mastery["count_to_20"] > 0.8


def test_practice_confirms_what_placement_sketched(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    tutor, probes = place(graph, specs, lambda c: graph.depth(c) <= 3)
    task = tutor.next_task()
    assert task is not None
    assert graph.depth(task.competency) <= 3
    assert task.level == "hard"
    assert tutor.state.mastery[task.competency] < MASTERED
