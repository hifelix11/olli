"""One learner's practice loop: select, generate, check, update. In memory for now."""

import random
from dataclasses import dataclass

from app.domain.generators.generate import generate_task
from app.domain.generators.models import GeneratorSpec, Task
from app.domain.graph.graph import CompetencyGraph
from app.domain.selection.select import BACKTRACK_AFTER, backtrack, level_for, select_next
from app.domain.tracing.learner import LearnerState


@dataclass
class SubmitResult:
    correct: bool
    backtracked_to: str | None = None


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
        self.practicable = set(specs)
        self.state = state or LearnerState.fresh(graph)
        self.rng = rng or random.Random()

    def next_task(self) -> Task | None:
        """None means everything practicable is mastered."""
        competency = select_next(self.graph, self.state, self.practicable)
        if competency is None:
            return None
        level = level_for(self.state.mastery[competency.id])
        return generate_task(self.specs[competency.id], level, self.rng)

    def submit(self, task: Task, answer: int | str) -> SubmitResult:
        competency = self.graph.get(task.competency)
        correct = answer == task.answer
        if task.options:
            # Choice tasks can be guessed: never below one over the number of options.
            p_guess = max(competency.bkt.p_guess, 1 / len(task.options))
            competency = competency.model_copy(
                update={"bkt": competency.bkt.model_copy(update={"p_guess": p_guess})}
            )
        self.state.record(competency, correct)
        backtracked_to = None
        if self.state.wrong_streak[competency.id] >= BACKTRACK_AFTER:
            weakest = backtrack(self.graph, self.state, competency, self.practicable)
            backtracked_to = weakest.id if weakest else None
        return SubmitResult(correct, backtracked_to)
