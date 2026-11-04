"""Pick what to practise next and step back to basics after repeated failure."""

from app.domain.graph.graph import Competency, CompetencyGraph
from app.domain.tracing.learner import LearnerState

MASTERED = 0.95  # mastery at or above this counts as secure
DOUBT = 0.3  # mastery a prerequisite drops to when we step back to it
BACKTRACK_AFTER = 3  # wrong answers in a row before stepping back


def select_next(graph: CompetencyGraph, state: LearnerState) -> Competency | None:
    """Not yet mastered, all prerequisites mastered. Most basic first, then closest to done."""
    mastery = state.mastery
    candidates = [
        c
        for c in graph
        if mastery[c.id] < MASTERED and all(mastery[p] >= MASTERED for p in c.prerequisites)
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


def backtrack(graph: CompetencyGraph, state: LearnerState, failed: Competency) -> Competency | None:
    """Doubt the weakest direct prerequisite so selection practises it again. Roots have none."""
    prerequisites = graph.prerequisites(failed.id)
    state.wrong_streak[failed.id] = 0
    if not prerequisites:
        return None
    weakest = min(prerequisites, key=lambda c: state.mastery[c.id])
    state.mastery[weakest.id] = min(state.mastery[weakest.id], DOUBT)
    return weakest
