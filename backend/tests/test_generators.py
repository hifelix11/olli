import random

import pytest

from app.domain.generators.generate import generate_task
from app.domain.generators.models import GeneratorSpec


def test_addition_respects_ranges_and_sum(specs: dict[str, GeneratorSpec]) -> None:
    spec = specs["add_within_20_with_carry"]
    rng = random.Random(0)
    for _ in range(200):
        task = generate_task(spec, "medium", rng)
        a, b = task.operands["a"], task.operands["b"]
        assert 5 <= a <= 9 and 2 <= b <= 9
        assert 11 <= a + b <= 20
        assert task.answer == a + b


def test_level_overrides_apply(specs: dict[str, GeneratorSpec]) -> None:
    spec = specs["add_within_20_with_carry"]
    rng = random.Random(0)
    for _ in range(200):
        task = generate_task(spec, "easy", rng)
        assert task.operands["a"] <= 7
        assert task.answer <= 14


def test_missing_addend(specs: dict[str, GeneratorSpec]) -> None:
    spec = specs["complement_to_10"]
    rng = random.Random(0)
    for _ in range(50):
        task = generate_task(spec, "medium", rng)
        assert task.operands["target"] == 10
        assert task.operands["a"] + task.answer == 10
        assert task.answer >= 1


def test_impossible_constraints_raise(specs: dict[str, GeneratorSpec]) -> None:
    spec = specs["add_within_10"].model_copy(update={"constraints": {"sum_min": 50}})
    with pytest.raises(ValueError, match="no valid tasks"):
        generate_task(spec, "medium", random.Random(0))
