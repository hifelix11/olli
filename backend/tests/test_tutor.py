"""Demo scenario: the system notices where a child is stuck and steps back."""

import random

import pytest

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


def test_fresh_learner_starts_at_a_root(graph: CompetencyGraph) -> None:
    chosen = select_next(graph, LearnerState.fresh(graph))
    assert chosen is not None
    assert chosen.id == "number_sequence_to_10"


def test_missing_generator_fails_loudly(graph: CompetencyGraph) -> None:
    with pytest.raises(LookupError, match="number_sequence_to_10"):
        Tutor(graph, specs={}).next_task()


def test_steps_back_after_repeated_failure_and_returns(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    tutor = Tutor(graph, specs, lena(graph), random.Random(1))

    task = tutor.next_task()
    assert task is not None and task.competency == GOAL

    for _ in range(3):
        task = tutor.next_task()
        assert task is not None and task.competency == GOAL
        assert tutor.submit(task, task.answer + 1) is False

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
