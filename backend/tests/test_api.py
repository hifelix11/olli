"""The learning loop over HTTP, against an in-memory SQLite database."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Attempt, Child, Mastery, TaskRow
from app.domain.generators.models import GeneratorSpec
from app.domain.graph.graph import CompetencyGraph

GOAL = "add_within_20_with_carry"


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
    child = client.post("/children", json={"name": "Lena", "sign": "fish"}).json()
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
    assert wrong["retry"] is True
    assert wrong["answer"] is None

    rows = client.get(f"/children/{child['id']}/mastery").json()
    assert len(rows) == 68
    by_id = {r["competency"]: r for r in rows}
    assert by_id["number_sequence_to_10"]["status"] == "in_progress"
    assert by_id[GOAL]["status"] == "not_started"


def test_placement_and_progress_over_http(
    client: TestClient, db: sessionmaker[Session], specs: dict[str, GeneratorSpec]
) -> None:
    child = client.post("/children", json={"name": "Lena", "sign": "fish"}).json()
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
    child = client.post("/children", json={"name": "Lena", "sign": "fish"}).json()
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


def answer(client: TestClient, child_id: str, task_id: str, value: object) -> dict[str, object]:
    res = client.post(f"/children/{child_id}/answers", json={"task_id": task_id, "answer": value})
    assert res.status_code == 200
    return res.json()


def test_second_try_counts_as_help(client: TestClient, db: sessionmaker[Session]) -> None:
    """Free input: a wrong first try earns one more. Only the first try moves the learner state."""
    child = client.post("/children", json={"name": "Lena", "sign": "fish"}).json()
    skip_placement(db, child["id"])
    task = client.get(f"/children/{child['id']}/next-task").json()
    assert task["options"] is None

    first = answer(client, child["id"], task["id"], -1)
    assert (first["correct"], first["retry"], first["answer"]) == (False, True, None)

    second = answer(client, child["id"], task["id"], solution(db, task["id"]))
    assert (second["correct"], second["retry"]) == (True, False)
    assert second["answer"] == solution(db, task["id"])
    assert second["p_known"] == first["p_known"]

    third = client.post(
        f"/children/{child['id']}/answers", json={"task_id": task["id"], "answer": 0}
    )
    assert third.status_code == 409

    with db() as session:
        tries = session.scalars(select(Attempt).where(Attempt.task_id == task["id"])).all()
        assert [(a.try_no, a.correct) for a in tries] == [(1, False), (2, True)]


def test_no_second_try_in_placement_or_after_dont_know(
    client: TestClient, db: sessionmaker[Session]
) -> None:
    child = client.post("/children", json={"name": "Lena", "sign": "fish"}).json()
    task = client.get(f"/children/{child['id']}/next-task").json()
    assert task["placement"] is True
    placed = answer(client, child["id"], task["id"], -1)
    assert placed["retry"] is False and placed["answer"] is not None

    skip_placement(db, child["id"])
    task = client.get(f"/children/{child['id']}/next-task").json()
    dont_know = answer(client, child["id"], task["id"], None)
    assert (dont_know["correct"], dont_know["retry"]) == (False, False)
    assert dont_know["answer"] == solution(db, task["id"])
    with db() as session:
        attempt = session.scalar(select(Attempt).where(Attempt.task_id == task["id"]))
        assert attempt is not None and attempt.answer is None


def test_mastered_reports_the_step_over_the_line(
    client: TestClient, db: sessionmaker[Session], graph: CompetencyGraph
) -> None:
    child = client.post("/children", json={"name": "Lena", "sign": "fish"}).json()
    skip_placement(db, child["id"])
    with db.begin() as session:
        for c in graph:
            p = 0.9 if c.id == GOAL else 0.99
            session.add(Mastery(child_id=child["id"], competency=c.id, p_known=p))

    task = client.get(f"/children/{child['id']}/next-task").json()
    assert task["competency"] == GOAL
    result = answer(client, child["id"], task["id"], solution(db, task["id"]))
    assert result["p_known"] >= 0.95
    assert result["mastered"] is True


def test_sign_must_be_known(client: TestClient) -> None:
    assert client.post("/children", json={"name": "Lena", "sign": "dragon"}).status_code == 422
