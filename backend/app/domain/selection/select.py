"""Pick what to practise next and step back to basics after repeated failure."""

from app.domain.graph.graph import Competency, CompetencyGraph
from app.domain.tracing.learner import LearnerState

MASTERED = 0.95  # mastery at or above this counts as secure
DOUBT = 0.3  # mastery a prerequisite drops to when we step back to it
BACKTRACK_AFTER = 3  # wrong answers in a row before stepping back


def select_next(
    graph: CompetencyGraph, state: LearnerState, practicable: set[str]
) -> Competency | None:
    """Not yet mastered, all prerequisites mastered. Most basic first, then closest to done.

    Only practicable competencies (those with a generator) are chosen. A prerequisite the app
    cannot practise does not block its successors.
    """
    mastery = state.mastery

    def secure(competency_id: str) -> bool:
        return competency_id not in practicable or mastery[competency_id] >= MASTERED

    candidates = [
        c
        for c in graph
        if c.id in practicable and not secure(c.id) and all(secure(p) for p in c.prerequisites)
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda c: (graph.depth(c.id), -mastery[c.id]))


def level_for(p_known: float) -> str:
    if p_known < 0.4:
        return "easy"
    if p_known < 0.75:
        return "medium"
    return "hard"


def backtrack(
    graph: CompetencyGraph, state: LearnerState, failed: Competency, practicable: set[str]
) -> Competency | None:
    """Doubt the weakest practicable direct prerequisite so selection practises it again."""
    prerequisites = [p for p in graph.prerequisites(failed.id) if p.id in practicable]
    state.wrong_streak[failed.id] = 0
    if not prerequisites:
        return None
    weakest = min(prerequisites, key=lambda c: state.mastery[c.id])
    state.mastery[weakest.id] = min(state.mastery[weakest.id], DOUBT)
    return weakest
