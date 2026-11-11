"""kind: clock. Read a full or half hour. params: hour (1..12). settings.minutes: subset of [0, 30].

Answers are times like "3:00" and "2:30". labels full and half name them,
with {hour} and {next_hour}: "{hour} Uhr", "halb {next_hour}".
Options: the time plus the two half hours around it (or the two full hours around a half hour).
"""

import random

from app.domain.generators.models import GeneratorSpec, Option, Task, choose, make_task


def option(spec: GeneratorSpec, hour: int, minute: int) -> Option:
    name = spec.label("full" if minute == 0 else "half", hour=hour, next_hour=hour % 12 + 1)
    return Option(value=f"{hour}:{minute:02d}", label=name)


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    hour = choose(list(s.params["hour"].values()), spec, level, rng)
    minute = rng.choice(s.settings.get("minutes", [0, 30]))
    before, after = (hour - 2) % 12 + 1, hour % 12 + 1
    others = [(before, 30), (hour, 30)] if minute == 0 else [(hour, 0), (after, 0)]
    options = [option(s, h, m) for h, m in [(hour, minute), *others]]
    rng.shuffle(options)
    operands: dict[str, int | str] = {"hour": hour, "minute": minute}
    return make_task(s, level, operands, f"{hour}:{minute:02d}", s.template(), options)
