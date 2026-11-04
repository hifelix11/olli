import pytest

from app.domain.graph.graph import BktParams
from app.domain.tracing import bkt

PARAMS = BktParams(p_init=0.2, p_learn=0.15, p_slip=0.1, p_guess=0.05)


def test_correct_answer_raises_mastery() -> None:
    # posterior 0.18 / (0.18 + 0.04) = 0.8182, then + (1 - 0.8182) * 0.15
    assert bkt.update(0.2, True, PARAMS) == pytest.approx(0.84545, abs=1e-4)


def test_wrong_answer_lowers_mastery() -> None:
    # posterior 0.02 / (0.02 + 0.76) = 0.0256, then + (1 - 0.0256) * 0.15
    assert bkt.update(0.2, False, PARAMS) == pytest.approx(0.17179, abs=1e-4)


def test_three_correct_answers_reach_mastery() -> None:
    p = PARAMS.p_init
    for _ in range(3):
        p = bkt.update(p, True, PARAMS)
    assert p > 0.95
