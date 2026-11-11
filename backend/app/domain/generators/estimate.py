"""kind: estimate. Scattered counters: roughly how many? The answer is the nearest anchor.

params: n. settings.anchors: the options, e.g. [5, 10, 15, 20]. Ties are left out.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    anchors: list[int] = sorted(s.settings["anchors"])
    candidates = []
    for n in s.params["n"].values():
        distances = sorted(abs(n - a) for a in anchors)
        if len(distances) == 1 or distances[0] < distances[1]:
            candidates.append(n)
    n = choose(candidates, spec, level, rng)
    answer = min(anchors, key=lambda a: abs(n - a))
    return make_task(s, level, {"n": n}, answer, s.template(), s.options(anchors))
