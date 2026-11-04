"""One learner's practice loop: select, generate, check, update. In memory for now."""

import random

from app.domain.generators.generate import generate_task
from app.domain.generators.models import GeneratorSpec, Task
from app.domain.graph.graph import CompetencyGraph
from app.domain.selection.select import BACKTRACK_AFTER, backtrack, level_for, select_next
from app.domain.tracing.learner import LearnerState


class Tutor:
    def __init__(
        self,
        graph: CompetencyGraph,
        specs: dict[str, GeneratorSpec],
        state: LearnerState | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self.graph = graph
        self.specs = specs
        self.state = state or LearnerState.fresh(graph)
        self.rng = rng or random.Random()

    def next_task(self) -> Task | None:
        """None means everything in the graph is mastered."""
        competency = select_next(self.graph, self.state)
        if competency is None:
            return None
        spec = self.specs.get(competency.id)
        if spec is None:
            raise LookupError(f"no generator for competency '{competency.id}'")
        level = level_for(self.state.mastery[competency.id])
        return generate_task(spec, level, self.rng)

    def submit(self, task: Task, answer: int) -> bool:
        competency = self.graph.get(task.competency)
        correct = answer == task.answer
        self.state.record(competency, correct)
        if self.state.wrong_streak[competency.id] >= BACKTRACK_AFTER:
            backtrack(self.graph, self.state, competency)
        return correct
