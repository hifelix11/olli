"""Learner state: mastery per competency plus the current run of wrong answers."""

from dataclasses import dataclass, field

from app.domain.graph.graph import Competency, CompetencyGraph
from app.domain.tracing import bkt


@dataclass
class LearnerState:
    mastery: dict[str, float]
    wrong_streak: dict[str, int] = field(default_factory=dict)

    @classmethod
    def fresh(cls, graph: CompetencyGraph) -> "LearnerState":
        return cls(mastery={c.id: c.bkt.p_init for c in graph})

    def record(self, competency: Competency, correct: bool) -> None:
        self.mastery[competency.id] = bkt.update(
            self.mastery[competency.id], correct, competency.bkt
        )
        self.wrong_streak[competency.id] = (
            0 if correct else self.wrong_streak.get(competency.id, 0) + 1
        )
