"""Load and save learner state. Only changed rows are written."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Mastery
from app.domain.graph.graph import CompetencyGraph
from app.domain.tracing.learner import LearnerState


def load_state(session: Session, graph: CompetencyGraph, child_id: str) -> LearnerState:
    state = LearnerState.fresh(graph)
    rows = session.scalars(select(Mastery).where(Mastery.child_id == child_id))
    for row in rows:
        state.mastery[row.competency] = row.p_known
        state.wrong_streak[row.competency] = row.wrong_streak
    return state


def save_state(session: Session, child_id: str, before: LearnerState, after: LearnerState) -> None:
    for competency, p_known in after.mastery.items():
        streak = after.wrong_streak.get(competency, 0)
        unchanged = p_known == before.mastery[competency] and streak == before.wrong_streak.get(
            competency, 0
        )
        if not unchanged:
            session.merge(
                Mastery(
                    child_id=child_id,
                    competency=competency,
                    p_known=p_known,
                    wrong_streak=streak,
                )
            )
