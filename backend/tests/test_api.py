"""The learning loop over HTTP, against an in-memory SQLite database."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base, Child, Mastery, TaskRow
from app.db.session import get_session
from app.domain.generators.models import GeneratorSpec
from app.domain.graph.graph import CompetencyGraph
from app.main import app

GOAL = "add_within_20_with_carry"


@pytest.fixture
def db() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(engine)
    engine.dispose()


@pytest.fixture
def client(db: sessionmaker[Session]) -> Iterator[TestClient]:
    def override() -> Iterator[Session]:
        with db.begin() as session:
            yield session

    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def solution(db: sessionmaker[Session], task_id: str) -> int | str:
    with db() as session:
        row = session.get(TaskRow, task_id)
        assert row is not None
        return row.payload["answer"]


def skip_placement(db: sessionmaker[Session], child_id: str) -> None:
    with db.begin() as session:
        child = session.get(Child, child_id)
        assert child is not None
        child.placement_done = True


def test_unknown_child_is_404(client: TestClient) -> None:
    assert client.get("/children/nope/next-task").status_code == 404


def test_loop_over_http(client: TestClient, db: sessionmaker[Session]) -> None:
    child = client.post("/children", json={"name": "Lena"}).json()
    skip_placement(db, child["id"])

    task = client.get(f"/children/{child['id']}/next-task").json()
    assert task["placement"] is False
    assert task["competency"] == "number_sequence_to_10"
    assert "answer" not in task

    answer = client.post(
        f"/children/{child['id']}/answers",
        json={"task_id": task["id"], "answer": str(solution(db, task["id"]))},
    ).json()
    assert answer["correct"] is True
    assert answer["p_known"] > 0.2

    again = client.post(
        f"/children/{child['id']}/answers", json={"task_id": task["id"], "answer": 0}
    )
    assert again.status_code == 409

    task = client.get(f"/children/{child['id']}/next-task").json()
    wrong = client.post(
        f"/children/{child['id']}/answers", json={"task_id": task["id"], "answer": -999}
    ).json()
    assert wrong["correct"] is False
    assert wrong["answer"] == solution(db, task["id"])

    rows = client.get(f"/children/{child['id']}/mastery").json()
    assert len(rows) == 68
    by_id = {r["competency"]: r for r in rows}
    assert by_id["number_sequence_to_10"]["status"] == "in_progress"
    assert by_id[GOAL]["status"] == "not_started"


def test_placement_and_progress_over_http(
    client: TestClient, db: sessionmaker[Session], specs: dict[str, GeneratorSpec]
) -> None:
    child = client.post("/children", json={"name": "Lena"}).json()
    progress = client.get(f"/children/{child['id']}/progress").json()
    assert progress == {
        "curriculum": "LehrplanPLUS Grundschule Mathematik 1/2",
        "grade": 1,
        "goal": 68,
        "checkable": len(specs),
        "mastered": 0,
        "in_progress": 0,
        "placement_done": False,
    }

    probes = 0
    while True:
        task = client.get(f"/children/{child['id']}/next-task").json()
        if not task["placement"]:
            break
        probes += 1
        assert probes < len(specs) // 2
        client.post(
            f"/children/{child['id']}/answers",
            json={"task_id": task["id"], "answer": solution(db, task["id"])},
        )

    progress = client.get(f"/children/{child['id']}/progress").json()
    assert progress["placement_done"] is True
    assert progress["mastered"] + progress["in_progress"] == len(specs)
    assert task["level"] == "hard"


def test_backtrack_over_http(
    client: TestClient, db: sessionmaker[Session], graph: CompetencyGraph
) -> None:
    child = client.post("/children", json={"name": "Lena"}).json()
    with db.begin() as session:
        for c in graph:
            p = 0.2 if c.id == GOAL else 0.99
            session.add(Mastery(child_id=child["id"], competency=c.id, p_known=p))

    for i in range(3):
        task = client.get(f"/children/{child['id']}/next-task").json()
        assert task["competency"] == GOAL
        result = client.post(
            f"/children/{child['id']}/answers", json={"task_id": task["id"], "answer": -1}
        ).json()
        assert result["backtracked_to"] == ("complement_to_10" if i == 2 else None)

    task = client.get(f"/children/{child['id']}/next-task").json()
    assert task["competency"] == "complement_to_10"
    assert task["level"] == "easy"

    with db() as session:
        doubted = session.scalar(
            select(Mastery).where(
                Mastery.child_id == child["id"], Mastery.competency == "complement_to_10"
            )
        )
        assert doubted is not None and doubted.p_known == 0.3
