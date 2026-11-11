"""Children, tasks, answers, mastery. The task's answer never leaves the backend.

A parent sees only their own children. Another parent's child is 404, not 403.
"""

from copy import deepcopy
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.account import guardian
from app.api.auth import Parent
from app.content import load_curriculum, load_generators, load_graph
from app.db.models import Attempt, Child, Mastery, TaskRow
from app.db.repository import load_state, save_state
from app.db.session import get_session
from app.domain.generators.models import Option, Task
from app.domain.selection.select import MASTERED
from app.domain.tutor import Tutor

router = APIRouter()
Db = Annotated[Session, Depends(get_session)]


# Pictures a child finds itself by, like the sign on a kindergarten peg. The frontend draws them.
Sign = Literal["sun", "moon", "star", "heart", "fish", "apple", "flower", "boat"]


class ChildIn(BaseModel):
    name: str
    sign: Sign


class ChildOut(BaseModel):
    id: str
    name: str
    sign: str


class TaskOut(BaseModel):
    id: str
    competency: str
    title: str
    kind: str
    level: str
    prompt: str
    operands: dict[str, int | str]
    options: list[Option] | None  # show the label, send back the value
    representations: list[str]
    placement: bool  # part of the placement check, not of practice


class AnswerIn(BaseModel):
    task_id: str
    answer: int | str | None  # None: "I don't know yet". Counts as wrong.


class AnswerOut(BaseModel):
    correct: bool
    answer: int | str | None  # the solution. None while a second try is open
    retry: bool  # the child may try once more
    p_known: float
    backtracked_to: str | None
    mastered: bool  # this answer made the competency mastered. Never in placement


class MasteryOut(BaseModel):
    competency: str
    title: str
    area: str
    p_known: float
    status: str  # mastered | in_progress | not_started
    practicable: bool  # False: no generator yet, the app cannot practise it


class ProgressOut(BaseModel):
    """How far the child is towards what the curriculum expects by the end of the grade."""

    curriculum: str
    grade: int
    goal: int  # competencies the curriculum expects
    checkable: int  # of those, the ones with a generator
    mastered: int
    in_progress: int
    placement_done: bool


def owned_child(child_id: str, session: Db, parent: Parent) -> Child:
    child = session.get(Child, child_id)
    if child is None or child.guardian_id != parent:
        raise HTTPException(404, "child not found")
    return child


OwnedChild = Annotated[Child, Depends(owned_child)]


def mastery_rows(session: Session, child_id: str) -> dict[str, Mastery]:
    return {
        r.competency: r
        for r in session.scalars(select(Mastery).where(Mastery.child_id == child_id))
    }


def status_of(row: Mastery | None) -> str:
    if row is None:
        return "not_started"
    return "mastered" if row.p_known >= MASTERED else "in_progress"


@router.get("/children", response_model=list[ChildOut])
def list_children(session: Db, parent: Parent) -> Any:
    return session.scalars(
        select(Child).where(Child.guardian_id == parent).order_by(Child.created_at)
    ).all()


@router.post("/children", response_model=ChildOut, status_code=201)
def create_child(body: ChildIn, session: Db, parent: Parent) -> Any:
    guardian(session, parent)
    child = Child(guardian_id=parent, name=body.name, sign=body.sign)
    session.add(child)
    session.flush()
    return child


@router.get("/children/{child_id}/next-task", response_model=TaskOut | None)
def next_task(child: OwnedChild, session: Db) -> Any:
    """None when every competency is mastered. A new child gets the placement check first."""
    graph = load_graph()
    state = load_state(session, graph, child.id)
    tutor = Tutor(graph, load_generators(), state, placing=not child.placement_done)
    task = tutor.next_task()
    child.placement_done = not tutor.placing
    if task is None:
        return None
    row = TaskRow(child_id=child.id, competency=task.competency, payload=task.model_dump())
    session.add(row)
    session.flush()
    return TaskOut(
        id=row.id,
        title=graph.get(task.competency).title,
        placement=tutor.placing,
        **task.model_dump(),
    )


@router.post("/children/{child_id}/answers", response_model=AnswerOut)
def submit_answer(child: OwnedChild, body: AnswerIn, session: Db) -> Any:
    """The first try updates the learner state. A second try is practice with help and does not."""
    row = session.get(TaskRow, body.task_id)
    if row is None or row.child_id != child.id:
        raise HTTPException(404, "task not found")
    task = Task(**row.payload)
    placing = not child.placement_done
    tries = session.scalars(select(Attempt).where(Attempt.task_id == row.id)).all()
    if tries and (len(tries) > 1 or not second_try(task, tries[0], placing)):
        raise HTTPException(409, "task already answered")

    graph = load_graph()
    before = load_state(session, graph, child.id)
    given = None if body.answer is None else coerce(body.answer, task.answer)
    after, backtracked_to = before, None
    if tries:
        correct = given == task.answer
    else:
        tutor = Tutor(graph, load_generators(), deepcopy(before), placing=placing)
        result = tutor.submit(task, given)
        correct, after, backtracked_to = result.correct, tutor.state, result.backtracked_to
        save_state(session, child.id, before, after)

    attempt = Attempt(
        task_id=row.id,
        try_no=len(tries) + 1,
        child_id=child.id,
        competency=task.competency,
        answer=body.answer,
        correct=correct,
    )
    session.add(attempt)
    retry = not tries and second_try(task, attempt, placing)
    p_before, p_after = before.mastery[task.competency], after.mastery[task.competency]
    return AnswerOut(
        correct=correct,
        answer=None if retry else task.answer,
        retry=retry,
        p_known=p_after,
        backtracked_to=backtracked_to,
        mastered=not placing and p_before < MASTERED <= p_after,
    )


def second_try(task: Task, first: Attempt, placing: bool) -> bool:
    """A wrong first answer earns one more try. Not in placement, not after "I don't know yet",
    not for choices: with two options the second try is a gift."""
    return not (first.correct or placing or first.answer is None or task.options)


@router.get("/children/{child_id}/mastery", response_model=list[MasteryOut])
def mastery(child: OwnedChild, session: Db) -> Any:
    graph = load_graph()
    practicable = set(load_generators())
    rows = mastery_rows(session, child.id)
    return [
        MasteryOut(
            competency=c.id,
            title=c.title,
            area=c.area,
            p_known=rows[c.id].p_known if c.id in rows else c.bkt.p_init,
            status=status_of(rows.get(c.id)),
            practicable=c.id in practicable,
        )
        for c in graph
    ]


@router.get("/children/{child_id}/progress", response_model=ProgressOut)
def progress(child: OwnedChild, session: Db) -> Any:
    curriculum = load_curriculum()
    checkable = curriculum.competencies & set(load_generators())
    rows = mastery_rows(session, child.id)
    statuses = [status_of(rows.get(c)) for c in checkable]
    return ProgressOut(
        curriculum=curriculum.title,
        grade=curriculum.grade,
        goal=len(curriculum.competencies),
        checkable=len(checkable),
        mastered=statuses.count("mastered"),
        in_progress=statuses.count("in_progress"),
        placement_done=child.placement_done,
    )


def coerce(given: int | str, expected: int | str) -> int | str:
    """A number typed into a text field arrives as a string. Compare numbers as numbers."""
    if isinstance(expected, int) and isinstance(given, str):
        try:
            return int(given.strip())
        except ValueError:
            return given
    return given
