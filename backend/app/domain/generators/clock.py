"""kind: clock. Read a full or half hour. params: hour (1..12). settings.minutes: subset of [0, 30].

Options: the time plus the two half hours around it (or the two full hours around a half hour).
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

PROMPT = "Wie spät ist es?"


def name(hour: int, minute: int) -> str:
    return f"{hour} Uhr" if minute == 0 else f"halb {hour % 12 + 1}"


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    hour = choose(list(s.params["hour"].values()), spec, level, rng)
    minute = rng.choice(s.settings.get("minutes", [0, 30]))
    answer = name(hour, minute)
    before, after = (hour - 2) % 12 + 1, hour % 12 + 1
    if minute == 0:
        options: list[int | str] = [answer, name(before, 30), name(hour, 30)]
    else:
        options = [answer, name(hour, 0), name(after, 0)]
    rng.shuffle(options)
    return make_task(s, level, {"hour": hour, "minute": minute}, answer, PROMPT, options)
