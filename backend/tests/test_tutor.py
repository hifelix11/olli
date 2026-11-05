"""Demo scenario: the system notices where a child is stuck and steps back."""

import random

from app.domain.generators.generate import generate_task
from app.domain.generators.models import GeneratorSpec, Task
from app.domain.graph.graph import CompetencyGraph
from app.domain.selection.select import MASTERED, select_next
from app.domain.tracing.learner import LearnerState
from app.domain.tutor import Tutor

GOAL = "add_within_20_with_carry"


def lena(graph: CompetencyGraph) -> LearnerState:
    """Everything secure except the goal."""
    state = LearnerState.fresh(graph)
    for competency_id in state.mastery:
        state.mastery[competency_id] = 0.99
    state.mastery[GOAL] = 0.2
    return state


def test_fresh_learner_starts_at_a_practicable_root(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    chosen = select_next(graph, LearnerState.fresh(graph), set(specs))
    assert chosen is not None
    assert chosen.id == "number_sequence_to_10"


def test_nothing_practicable_means_nothing_to_do(graph: CompetencyGraph) -> None:
    assert Tutor(graph, specs={}).next_task() is None


def test_unpracticable_prerequisite_does_not_block(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    """add_within_10 needs addition_meaning, which has no generator yet."""
    assert "addition_meaning" not in specs
    state = LearnerState.fresh(graph)
    for competency_id in [
        "number_sequence_to_10",
        "subitize_to_5",
        "count_objects_to_10",
        "structured_quantities_twenty_field",
        "number_decomposition_to_10",
    ]:
        state.mastery[competency_id] = 0.99
    chosen = select_next(graph, state, set(specs))
    assert chosen is not None
    assert chosen.id in {"add_within_10", "complement_to_10", "read_write_numbers_to_20"}
    assert graph.get("add_within_10").id in {
        c.id
        for c in graph
        if c.id in specs
        and all(p not in specs or state.mastery[p] >= MASTERED for p in c.prerequisites)
    }


def test_steps_back_after_repeated_failure_and_returns(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    tutor = Tutor(graph, specs, lena(graph), random.Random(1))

    task = tutor.next_task()
    assert task is not None and task.competency == GOAL

    for _ in range(3):
        task = tutor.next_task()
        assert task is not None and task.competency == GOAL
        assert tutor.submit(task, task.answer + 1).correct is False

    task = tutor.next_task()
    assert task is not None and task.competency == "complement_to_10"
    assert task.level == "easy"

    practised: list[Task] = []
    while task is not None and task.competency != GOAL:
        practised.append(task)
        tutor.submit(task, task.answer)
        task = tutor.next_task()

    assert task is not None and task.competency == GOAL
    assert {t.competency for t in practised} == {"complement_to_10"}
    assert tutor.state.mastery["complement_to_10"] >= MASTERED


def test_everything_mastered_ends_the_session(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    state = LearnerState.fresh(graph)
    for competency_id in state.mastery:
        state.mastery[competency_id] = 0.99
    assert Tutor(graph, specs, state).next_task() is None


def test_choice_tasks_raise_guess_rate(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    competency = graph.get("compare_numbers_to_20")
    task = generate_task(specs[competency.id], "medium", random.Random(0))

    guessable = LearnerState.fresh(graph)
    Tutor(graph, specs, guessable).submit(task, task.answer)

    free = LearnerState.fresh(graph)
    free.record(competency, True)

    assert free.mastery[competency.id] > guessable.mastery[competency.id] > competency.bkt.p_init
