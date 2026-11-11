"""kind: sequence_gap. A number sequence with one gap.

params: start, step. settings: length (4), min_value (0), max_value (20),
directions (["forward"]), gap ("any" or "end").
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    st = s.settings
    length = st.get("length", 4)
    lo, hi = st.get("min_value", 0), st.get("max_value", 20)
    candidates = []
    for direction in st.get("directions", ["forward"]):
        sign = 1 if direction == "forward" else -1
        for start in s.params["start"].values():
            for step in s.params["step"].values():
                seq = [start + i * step * sign for i in range(length)]
                if all(lo <= v <= hi for v in seq):
                    candidates.append((seq, step, direction))
    seq, step, direction = choose(candidates, spec, level, rng)
    gap = length - 1 if st.get("gap") == "end" else rng.randrange(length)
    shown = ", ".join("_" if i == gap else str(v) for i, v in enumerate(seq))
    operands: dict[str, int | str] = {"sequence": shown, "step": step, "direction": direction}
    return make_task(s, level, operands, seq[gap], s.template())
