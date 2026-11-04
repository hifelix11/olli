import random

import pytest

from app.domain.generators.generate import generate_task
from app.domain.generators.models import GeneratorSpec

LEVELS = ["easy", "medium", "hard"]


def test_every_spec_generates_at_every_level(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    for spec in specs.values():
        for level in LEVELS:
            for _ in range(50):
                task = generate_task(spec, level, rng)
                assert task.prompt
                if task.options is not None:
                    assert task.answer in task.options


def test_addition_respects_ranges_and_sum(specs: dict[str, GeneratorSpec]) -> None:
    spec = specs["add_within_20_with_carry"]
    rng = random.Random(0)
    for _ in range(200):
        task = generate_task(spec, "medium", rng)
        a, b = int(task.operands["a"]), int(task.operands["b"])
        assert 5 <= a <= 9 and 2 <= b <= 9
        assert 11 <= a + b <= 20
        assert task.answer == a + b
        assert task.prompt == f"{a} + {b} = ?"


def test_level_overrides_apply(specs: dict[str, GeneratorSpec]) -> None:
    spec = specs["add_within_20_with_carry"]
    rng = random.Random(0)
    for _ in range(200):
        task = generate_task(spec, "easy", rng)
        assert int(task.operands["a"]) <= 7
        assert int(task.answer) <= 14


def test_no_carry_and_borrow_constraints(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    for _ in range(200):
        task = generate_task(specs["add_within_20_no_carry"], "medium", rng)
        a, b = int(task.operands["a"]), int(task.operands["b"])
        assert a % 10 + b % 10 <= 9
        task = generate_task(specs["subtract_within_20_with_carry"], "medium", rng)
        a, b = int(task.operands["a"]), int(task.operands["b"])
        assert a % 10 < b % 10 and a - b >= 1


def test_variants_cover_both_forms(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    seen = set()
    for _ in range(100):
        task = generate_task(specs["subtract_ten_and_ones_to_20"], "medium", rng)
        a, b = int(task.operands["a"]), int(task.operands["b"])
        assert b == 10 or a - b == 10
        seen.add("minus_ten" if b == 10 else "to_ten")
    assert seen == {"minus_ten", "to_ten"}


def test_missing_number_forms_hold(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    forms = set()
    for _ in range(200):
        task = generate_task(specs["missing_number_to_20"], "medium", rng)
        a, b, c = (int(task.operands[k]) for k in "abc")
        assert a + b == c
        hidden = {"a+_=c": b, "_+b=c": a, "c-_=a": b, "_-b=a": c}[str(task.operands["form"])]
        assert task.answer == hidden
        forms.add(task.operands["form"])
    assert len(forms) == 4


def test_decomposition_uses_custom_prompt(specs: dict[str, GeneratorSpec]) -> None:
    task = generate_task(specs["number_decomposition_to_10"], "medium", random.Random(0))
    a, c = task.operands["a"], task.operands["c"]
    assert task.prompt == f"{c} = {a} + _"


def test_sequence_gap_answer_fits_sequence(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    for _ in range(200):
        task = generate_task(specs["count_in_steps_to_20"], "medium", rng)
        shown = str(task.operands["sequence"]).replace("_", str(task.answer))
        values = [int(v) for v in shown.split(", ")]
        diffs = {values[i + 1] - values[i] for i in range(len(values) - 1)}
        assert len(diffs) == 1
        assert abs(diffs.pop()) == task.operands["step"]


def test_check_equation_answer_is_truthful(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    for _ in range(200):
        task = generate_task(specs["check_results"], "medium", rng)
        a, b, shown = (int(task.operands[k]) for k in ("a", "b", "result"))
        true = a + b if task.operands["op"] == "+" else a - b
        assert task.answer == ("richtig" if shown == true else "falsch")


def test_chance_vocabulary(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    answers = set()
    for _ in range(200):
        task = generate_task(specs["chance_vocabulary"], "medium", rng)
        answers.add(task.answer)
    assert answers == {"sicher", "möglich", "unmöglich"}


def test_impossible_constraints_raise(specs: dict[str, GeneratorSpec]) -> None:
    spec = specs["add_within_10"].model_copy(update={"constraints": {"sum_min": 50}})
    with pytest.raises(ValueError, match="no valid tasks"):
        generate_task(spec, "medium", random.Random(0))


def test_answer_type_mismatch_is_rejected(specs: dict[str, GeneratorSpec]) -> None:
    spec = specs["compare_numbers_to_20"].model_copy(update={"answer": "free_input"})
    with pytest.raises(ValueError, match="answer type"):
        generate_task(spec, "medium", random.Random(0))
