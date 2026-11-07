"""kind: time_span. Whole hours between two times, or a time some hours later.

params: start, hours. settings.forms: subset of [duration, later]. settings.max_hour (12).
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

PROMPTS = {
    "duration": "Von {start} Uhr bis {end} Uhr. Wie viele Stunden sind das?",
    "later": "Es ist {start} Uhr. Wie spät ist es {hours} {hours_word} später?",
}


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    form = rng.choice(s.settings.get("forms", ["duration", "later"]))
    max_hour = s.settings.get("max_hour", 12)
    pairs = [
        (start, hours)
        for start in s.params["start"].values()
        for hours in s.params["hours"].values()
        if start + hours <= max_hour
    ]
    start, hours = choose(pairs, spec, level, rng)
    operands: dict[str, int | str] = {
        "start": start,
        "hours": hours,
        "end": start + hours,
        "form": form,
        "hours_word": "Stunde" if hours == 1 else "Stunden",
    }
    answer = hours if form == "duration" else start + hours
    return make_task(s, level, operands, answer, PROMPTS[form])
