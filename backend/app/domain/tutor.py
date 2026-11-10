"""One learner's loop: place or select, generate, check, update. In memory for now."""

import random
from dataclasses import dataclass

from app.domain.generators.generate import generate_task
from app.domain.generators.models import GeneratorSpec, Task
from app.domain.graph.graph import CompetencyGraph
from app.domain.selection.placement import PLACEMENT_LEVEL, place_next
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
        placing: bool = False,
    ) -> None:
        self.graph = graph
        self.specs = specs
        self.practicable = set(specs)
        self.state = state or LearnerState.fresh(graph)
        self.rng = rng or random.Random()
        self.placing = placing  # placement check first; turns False once nothing is left to probe

    def next_task(self) -> Task | None:
        """None means everything practicable is mastered."""
        if self.placing:
            competency = place_next(self.graph, self.state, self.practicable)
            if competency is not None:
                return generate_task(self.specs[competency.id], PLACEMENT_LEVEL, self.rng)
            self.placing = False
        competency = select_next(self.graph, self.state, self.practicable)
        if competency is None:
            return None
        level = level_for(self.state.mastery[competency.id])
        return generate_task(self.specs[competency.id], level, self.rng)

    def submit(self, task: Task, answer: int | str | None) -> SubmitResult:
        """None: the child does not know yet. Counts as wrong."""
        competency = self.graph.get(task.competency)
        correct = answer == task.answer
        if task.options:
            # Choice tasks can be guessed: never below one over the number of options.
            p_guess = max(competency.bkt.p_guess, 1 / len(task.options))
            competency = competency.model_copy(
                update={"bkt": competency.bkt.model_copy(update={"p_guess": p_guess})}
            )
        self.state.record(competency, correct)
        if self.placing:
            if correct:
                # Whoever solves this also has what it is built on.
                for prerequisite in self.graph.ancestors(competency.id):
                    if prerequisite.id in self.practicable:
                        self.state.record(prerequisite, True)
            return SubmitResult(correct)
        backtracked_to = None
        if self.state.wrong_streak[competency.id] >= BACKTRACK_AFTER:
            weakest = backtrack(self.graph, self.state, competency, self.practicable)
            backtracked_to = weakest.id if weakest else None
        return SubmitResult(correct, backtracked_to)
