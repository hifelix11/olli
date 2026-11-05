"""Children, tasks, answers, mastery. The task's answer never leaves the backend."""

from copy import deepcopy
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content import load_generators, load_graph
from app.db.models import Attempt, Child, Mastery, TaskRow
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


def get_child(session: Session, child_id: str) -> Child:
    child = session.get(Child, child_id)
    if child is None:
        raise HTTPException(404, "child not found")
    return child


@router.post("/children", response_model=ChildOut, status_code=201)
def create_child(body: ChildIn, session: Db) -> Any:
    child = Child(name=body.name)
    session.add(child)
    session.flush()
    return child


@router.get("/children/{child_id}/next-task", response_model=TaskOut | None)
def next_task(child_id: str, session: Db) -> Any:
    """None when every competency is mastered."""
    get_child(session, child_id)
    graph = load_graph()
    tutor = Tutor(graph, load_generators(), load_state(session, graph, child_id))
    task = tutor.next_task()
    if task is None:
        return None
    row = TaskRow(child_id=child_id, competency=task.competency, payload=task.model_dump())
    session.add(row)
    session.flush()
    return TaskOut(id=row.id, title=graph.get(task.competency).title, **task.model_dump())


@router.post("/children/{child_id}/answers", response_model=AnswerOut)
def submit_answer(child_id: str, body: AnswerIn, session: Db) -> Any:
    get_child(session, child_id)
    row = session.get(TaskRow, body.task_id)
    if row is None or row.child_id != child_id:
        raise HTTPException(404, "task not found")
    if session.scalar(select(Attempt.id).where(Attempt.task_id == row.id)):
        raise HTTPException(409, "task already answered")

    graph = load_graph()
    task = Task(**row.payload)
    before = load_state(session, graph, child_id)
    tutor = Tutor(graph, load_generators(), deepcopy(before))
    result = tutor.submit(task, coerce(body.answer, task.answer))

    save_state(session, child_id, before, tutor.state)
    session.add(
        Attempt(
            task_id=row.id,
            child_id=child_id,
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
def mastery(child_id: str, session: Db) -> Any:
    get_child(session, child_id)
    graph = load_graph()
    practicable = set(load_generators())
    rows = {
        r.competency: r
        for r in session.scalars(select(Mastery).where(Mastery.child_id == child_id))
    }
    out = []
    for c in graph:
        row = rows.get(c.id)
        p_known = row.p_known if row else c.bkt.p_init
        status = (
            "not_started" if row is None else "mastered" if p_known >= MASTERED else "in_progress"
        )
        out.append(
            MasteryOut(
                competency=c.id,
                title=c.title,
                area=c.area,
                p_known=p_known,
                status=status,
                practicable=c.id in practicable,
            )
        )
    return out


def coerce(given: int | str, expected: int | str) -> int | str:
    """A number typed into a text field arrives as a string. Compare numbers as numbers."""
    if isinstance(expected, int) and isinstance(given, str):
        try:
            return int(given.strip())
        except ValueError:
            return given
    return given
