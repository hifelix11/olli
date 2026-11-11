"""kind: time_span. Whole hours between two times, or a time some hours later.

params: start, hours. settings.forms: subset of [duration, later]. settings.max_hour (12).
prompts: duration, later. label hours names the span, singular and plural: {span}.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task


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
    }
    answer = hours if form == "duration" else start + hours
    words = {"span": s.label("hours", n=hours)}
    return make_task(s, level, operands, answer, s.template(form), words=words)
