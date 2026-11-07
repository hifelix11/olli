"""kind: bar_chart. Read a small chart (or table) of three categories.

settings.sets: list of {title, categories} (plural, single words).
settings.forms: subset of [most, least, how_many, wrong_bar].
params: value (one per category, all distinct).
wrong_bar shows the counted data in the prompt and draws one bar wrong.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, make_task

PROMPTS = {
    "most": "Wovon gibt es am meisten?",
    "least": "Wovon gibt es am wenigsten?",
    "how_many": "Wie viele {target} sind es?",
    "wrong_bar": "Gezählt wurden {counted}. Welche Säule stimmt nicht?",
}


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    data = rng.choice(s.settings["sets"])
    categories: list[str] = data["categories"]
    form = rng.choice(s.settings.get("forms", ["most"]))
    values = rng.sample(list(s.params["value"].values()), len(categories))
    shown = list(values)
    options: list[int | str] = list(categories)
    target = ""
    counted = ""
    if form == "most":
        answer: int | str = categories[values.index(max(values))]
    elif form == "least":
        answer = categories[values.index(min(values))]
    elif form == "how_many":
        target = rng.choice(categories)
        answer = values[categories.index(target)]
        options = sorted(values)
    else:
        i = rng.randrange(len(categories))
        shown[i] = max(0, values[i] + rng.choice([-2, -1, 1, 2]))
        if shown[i] == values[i]:
            shown[i] += 1
        answer = categories[i]
        counted = ", ".join(f"{c} {v}" for c, v in zip(categories, values, strict=True))
    operands: dict[str, int | str] = {
        "title": data["title"],
        "categories": " ".join(categories),
        "values": " ".join(str(v) for v in shown),
        "ask": form,
        "target": target,
        "counted": counted,
    }
    return make_task(s, level, operands, answer, PROMPTS[form], options)
