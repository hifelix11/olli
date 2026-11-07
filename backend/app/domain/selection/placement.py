"""Placement check: find out where a new learner stands before practice starts.

Practice works bottom-up and would make an advanced child solve trivial tasks for sessions.
The placement check probes top-down instead: a correct answer also counts for every
prerequisite, a wrong answer rules out everything built on top. Probing starts in the
middle of the graph and narrows in like a binary search over depth. The graph bounds the
number of probes: a beginner gets one per root, a learner who knows everything about
one per sink (a competency with no practicable successor).
"""

from app.domain.graph.graph import Competency, CompetencyGraph
from app.domain.tracing.learner import LearnerState

PLACEMENT_LEVEL = "medium"


def place_next(
    graph: CompetencyGraph, state: LearnerState, practicable: set[str]
) -> Competency | None:
    """Unobserved, nothing failed below it, depth between deepest success and shallowest failure.

    None when every practicable competency is observed or sits above a failed one.
    """

    def failed(competency_id: str) -> bool:
        return state.observed(competency_id) and state.wrong_streak[competency_id] > 0

    candidates = [
        c
        for c in graph
        if c.id in practicable
        and not state.observed(c.id)
        and not any(failed(p.id) for p in graph.ancestors(c.id) if p.id in practicable)
    ]
    if not candidates:
        return None

    depths = {c: graph.depth(c) for c in practicable}
    succeeded = [depths[c] for c in practicable if state.observed(c) and not failed(c)]
    failures = [depths[c] for c in practicable if failed(c)]
    low = max(succeeded, default=-1)
    high = min(failures, default=max(depths.values()) + 1)
    target = (low + high) // 2
    return min(candidates, key=lambda c: (abs(depths[c.id] - target), -depths[c.id]))
