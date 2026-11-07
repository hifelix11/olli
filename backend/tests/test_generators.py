import random

import pytest

from app.domain.generators.generate import generate_task
from app.domain.generators.models import GeneratorSpec
from app.domain.graph.graph import CompetencyGraph

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


# ---------- the kinds behind the picture, text and measurement competencies ----------

Cell = tuple[int, int]


def cells_of(text: str | int) -> set[Cell]:
    return {(int(x), int(y)) for x, y in (c.split(",") for c in str(text).split())}


def marks_of(text: str | int) -> dict[str, Cell]:
    marks = {}
    for mark in str(text).split():
        letter, cell = mark.split(":")
        marks[letter] = next(iter(cells_of(cell)))
    return marks


def test_only_the_word_problem_pool_has_no_generator(
    graph: CompetencyGraph, specs: dict[str, GeneratorSpec]
) -> None:
    assert {c.id for c in graph} - set(specs) == {"word_problems_to_10", "word_problems_to_20"}


def test_item_banks_are_consistent(specs: dict[str, GeneratorSpec]) -> None:
    """Every hand-written item, not only the drawn ones: the answer is one of distinct options."""
    for spec in specs.values():
        if spec.kind != "item_choice":
            continue
        for item in spec.settings["items"]:
            options = item.get("options", spec.settings.get("options"))
            assert item["answer"] in options, (spec.id, item["prompt"])
            assert len(options) == len(set(options)) >= 2, (spec.id, item["prompt"])


def test_word_problem_computes_the_answer(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    for spec_id in ("quantity_word_problems", "combinatorics_simple"):
        for _ in range(100):
            task = generate_task(specs[spec_id], "medium", rng)
            a, b = int(task.operands["a"]), int(task.operands["b"])
            expected = {"+": a + b, "−": a - b, "×": a * b}[str(task.operands["op"])]
            assert task.answer == expected >= 0
            assert "{" not in task.prompt


def test_picture_equation_matches_the_action(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    for _ in range(100):
        task = generate_task(specs["picture_to_equation"], "medium", rng)
        a, b, op = task.operands["a"], task.operands["b"], task.operands["op"]
        assert task.answer == f"{a} {op} {b}"
        assert task.options is not None and len(set(task.options)) == 3
        assert ("dazu" in task.prompt) == (op == "+")


def test_plus_minus_mixes_operations(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    ops = set()
    for _ in range(100):
        task = generate_task(specs["fluency_plus_minus_to_20"], "hard", rng)
        a, b, op = int(task.operands["a"]), int(task.operands["b"]), task.operands["op"]
        ops.add(op)
        assert task.answer == (a + b if op == "+" else a - b)
        assert (a % 10 + b % 10 >= 10) if op == "+" else (a % 10 < b % 10)
    assert ops == {"+", "−"}


def test_clock_names_full_and_half_hours(specs: dict[str, GeneratorSpec]) -> None:
    from app.domain.generators.clock import name

    assert (name(3, 0), name(3, 30), name(12, 30)) == ("3 Uhr", "halb 4", "halb 1")
    rng = random.Random(0)
    for _ in range(100):
        task = generate_task(specs["clock_full_half_hours"], "medium", rng)
        assert task.answer == name(int(task.operands["hour"]), int(task.operands["minute"]))
        assert task.options is not None and len(set(task.options)) == 3


def test_time_span_forms(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    for _ in range(100):
        task = generate_task(specs["time_spans_hours"], "medium", rng)
        start, hours, end = (int(task.operands[k]) for k in ("start", "hours", "end"))
        assert end == start + hours <= 12
        assert task.answer == (hours if task.operands["form"] == "duration" else end)


def test_calendar_neighbours(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    cycles = specs["calendar_basics"].settings["cycles"]
    for _ in range(100):
        task = generate_task(specs["calendar_basics"], "medium", rng)
        item = task.operands["item"]
        items = next(c["items"] for c in cycles if item in c["items"])
        step = 1 if task.operands["direction"] == "after" else -1
        assert task.answer == items[(items.index(item) + step) % len(items)]
        assert task.options is not None and item not in task.options


def test_money_amount_sums_the_pieces(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    units = set()
    for _ in range(100):
        task = generate_task(specs["money_coins_notes"], "medium", rng)
        coins = [int(v) for v in str(task.operands["coins"]).split()]
        assert task.answer == sum(coins) <= 20
        assert coins == sorted(coins, reverse=True)
        units.add(task.operands["unit"])
    assert units == {"€", "ct"}


def test_money_exchange_divides_evenly(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    for _ in range(100):
        task = generate_task(specs["money_compare_exchange"], "medium", rng)
        amount, value = int(task.operands["amount"]), int(task.operands["value"])
        assert amount % value == 0
        assert task.answer == amount // value >= 2


def test_compare_lengths(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    for _ in range(100):
        task = generate_task(specs["compare_lengths"], "medium", rng)
        a, b, ask = int(task.operands["a"]), int(task.operands["b"]), task.operands["ask"]
        if a == b:
            assert task.answer == "gleich lang"
        else:
            longer = "A" if a > b else "B"
            assert task.answer == (longer if ask == "longer" else {"A": "B", "B": "A"}[longer])


def test_compare_quantities_keeps_the_unit(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    for _ in range(100):
        task = generate_task(specs["order_quantities"], "medium", rng)
        a, b, unit, ask = (task.operands[k] for k in ("a", "b", "unit", "ask"))
        winner = max(int(a), int(b)) if ask == "more" else min(int(a), int(b))
        assert task.answer == f"{winner} {unit}"
        assert task.options == [f"{a} {unit}", f"{b} {unit}"]


def test_shape_name_options_never_overlap(specs: dict[str, GeneratorSpec]) -> None:
    """A square is also a rectangle and a quadrilateral: no option may be another name for it."""
    from app.domain.generators.shapes import NAMES, family

    by_name = {v: k for k, v in NAMES.items()}
    rng = random.Random(0)
    for _ in range(100):
        task = generate_task(specs["plane_shapes"], "medium", rng)
        assert task.answer == NAMES[str(task.operands["shapes"])]
        assert task.options is not None and len(task.options) == 3
        assert len({tuple(family(by_name[str(o)])) for o in task.options}) == 3


def test_shape_count(specs: dict[str, GeneratorSpec]) -> None:
    from app.domain.generators.shapes import CORNERS

    rng = random.Random(0)
    for _ in range(100):
        task = generate_task(specs["shape_properties"], "medium", rng)
        assert task.answer == CORNERS[str(task.operands["shapes"])] >= 3


def test_pattern_gap_follows_the_repeat(specs: dict[str, GeneratorSpec]) -> None:
    from app.domain.generators.shapes import NAMES

    by_name = {v: k for k, v in NAMES.items()}
    rng = random.Random(0)
    for level in LEVELS:
        for _ in range(100):
            task = generate_task(specs["geometric_patterns"], level, rng)
            row = str(task.operands["shapes"]).split()
            row[row.index("_")] = by_name[str(task.answer)]
            periods = [
                p
                for p in range(1, len(row))
                if all(row[i] == row[i + p] for i in range(len(row) - p))
            ]
            assert periods and 2 <= min(periods) <= 3


def test_grid_path_marks_the_goal(specs: dict[str, GeneratorSpec]) -> None:
    from app.domain.generators.grid_path import walk

    rng = random.Random(0)
    for level in LEVELS:
        for _ in range(100):
            task = generate_task(specs["follow_paths"], level, rng)
            width, height = int(task.operands["width"]), int(task.operands["height"])
            start = next(iter(cells_of(task.operands["start"])))
            marks = marks_of(task.operands["marks"])
            legs = []
            for part in str(task.operands["legs"]).replace(" und ", ", ").split(", "):
                steps, direction = part.split(" nach ")
                legs.append((direction, int(steps)))
            assert marks[str(task.answer)] == walk(start, legs)
            assert all(0 <= x < width and 0 <= y < height for x, y in marks.values())
            assert len(set(marks.values())) == 3 and start not in marks.values()


def test_grid_position_relation_holds(specs: dict[str, GeneratorSpec]) -> None:
    from app.domain.generators.grid_position import RELATIONS

    rng = random.Random(0)
    for _ in range(100):
        task = generate_task(specs["position_words"], "medium", rng)
        x, y = next(iter(cells_of(task.operands["start"])))
        dx, dy = RELATIONS[str(task.operands["relation"])]
        assert marks_of(task.operands["marks"])[str(task.answer)] == (x + dx, y + dy)


def test_symmetry_answer_is_truthful(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    answers = set()
    for _ in range(100):
        task = generate_task(specs["symmetry_basics"], "medium", rng)
        width = int(task.operands["width"])
        cells = cells_of(task.operands["cells"])
        mirrored = {(width - 1 - x, y) for x, y in cells}
        assert task.answer == ("ja" if mirrored == cells else "nein")
        answers.add(task.answer)
    assert answers == {"ja", "nein"}


def test_grid_copy_answer_is_truthful(specs: dict[str, GeneratorSpec]) -> None:
    from app.domain.generators.figures import normalized

    rng = random.Random(0)
    answers = set()
    for _ in range(100):
        task = generate_task(specs["copy_shapes_on_grid"], "medium", rng)
        cells, copy = cells_of(task.operands["cells"]), cells_of(task.operands["copy"])
        assert task.answer == ("ja" if normalized(copy) == normalized(cells) else "nein")
        assert len(copy) == len(cells)
        answers.add(task.answer)
    assert answers == {"ja", "nein"}


def test_switch_representation_carries_its_form(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    forms = set()
    for _ in range(100):
        task = generate_task(specs["switch_representations_to_20"], "medium", rng)
        form, n = str(task.operands["form"]), int(task.operands["n"])
        forms.add(form)
        assert task.answer == n
        pictures = {"twenty_field": ["twenty_field"], "number_line": ["number_line"]}
        assert task.representations == pictures.get(form, ["plain"])
        if form == "tens_ones":
            assert n >= 10 and int(task.operands["tens"]) * 10 + int(task.operands["ones"]) == n
    assert len(forms) == 4


def test_estimate_answers_nearest_anchor(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    for _ in range(100):
        task = generate_task(specs["estimate_quantities_to_20"], "medium", rng)
        n = int(task.operands["n"])
        assert task.answer == min([5, 10, 15, 20], key=lambda a: abs(n - a))


def test_bar_chart_forms(specs: dict[str, GeneratorSpec]) -> None:
    rng = random.Random(0)
    forms = set()
    for spec_id in ("read_tables_charts", "build_charts"):
        for _ in range(100):
            task = generate_task(specs[spec_id], "medium", rng)
            cats = str(task.operands["categories"]).split()
            vals = [int(v) for v in str(task.operands["values"]).split()]
            ask = str(task.operands["ask"])
            forms.add(ask)
            if ask == "most":
                assert task.answer == cats[vals.index(max(vals))]
            elif ask == "least":
                assert task.answer == cats[vals.index(min(vals))]
            elif ask == "how_many":
                assert task.answer == vals[cats.index(str(task.operands["target"]))]
            else:
                counted = dict(p.rsplit(" ", 1) for p in str(task.operands["counted"]).split(", "))
                wrong = [c for c, v in zip(cats, vals, strict=True) if int(counted[c]) != v]
                assert wrong == [task.answer]
    assert forms == {"most", "least", "how_many", "wrong_bar"}
