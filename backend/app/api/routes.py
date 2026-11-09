"""Children, tasks, answers, mastery. The task's answer never leaves the backend.

A parent sees only their own children. Another parent's child is 404, not 403.
"""

from copy import deepcopy
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import Parent
from app.content import load_curriculum, load_generators, load_graph
from app.db.models import Attempt, Child, Guardian, Mastery, TaskRow
from app.db.repository import load_state, save_state
from app.db.session import get_session
from app.domain.generators.models import Task
from app.domain.selection.select import MASTERED
from app.domain.tutor import Tutor

router = APIRouter()
Db = Annotated[Session, Depends(get_session)]


class ChildIn(BaseModel):
    name: str


class ChildOut(BaseModel):
    id: str
    name: str


class TaskOut(BaseModel):
    id: str
    competency: str
    title: str
    kind: str
    level: str
    prompt: str
    operands: dict[str, int | str]
    options: list[int | str] | None
    representations: list[str]
    placement: bool  # part of the placement check, not of practice


class AnswerIn(BaseModel):
    task_id: str
    answer: int | str


class AnswerOut(BaseModel):
    correct: bool
    answer: int | str
    p_known: float
    backtracked_to: str | None


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
    if session.get(Guardian, parent) is None:
        session.add(Guardian(id=parent))
        session.flush()
    child = Child(guardian_id=parent, name=body.name)
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
    row = session.get(TaskRow, body.task_id)
    if row is None or row.child_id != child.id:
        raise HTTPException(404, "task not found")
    if session.scalar(select(Attempt.id).where(Attempt.task_id == row.id)):
        raise HTTPException(409, "task already answered")

    graph = load_graph()
    task = Task(**row.payload)
    before = load_state(session, graph, child.id)
    tutor = Tutor(graph, load_generators(), deepcopy(before), placing=not child.placement_done)
    result = tutor.submit(task, coerce(body.answer, task.answer))

    save_state(session, child.id, before, tutor.state)
    session.add(
        Attempt(
            task_id=row.id,
            child_id=child.id,
            competency=task.competency,
            answer=body.answer,
            correct=result.correct,
        )
    )
    return AnswerOut(
        correct=result.correct,
        answer=task.answer,
        p_known=tutor.state.mastery[task.competency],
        backtracked_to=result.backtracked_to,
    )


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
