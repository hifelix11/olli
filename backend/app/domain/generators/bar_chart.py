"""kind: bar_chart. Read a small chart (or table) of three categories.

settings.sets: list of {title, categories}, all IDs with labels (categories plural, single words).
settings.forms: subset of [most, least, how_many, wrong_bar]. prompts: one per form.
params: value (one per category, all distinct).
how_many names the category as {name}. wrong_bar lists the counted data as {tally}
and draws one bar wrong. Answers are category IDs, for how_many the number.
The chart shows labels: operands title and categories carry them.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, make_task


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    data = rng.choice(s.settings["sets"])
    categories: list[str] = data["categories"]
    names = [s.label(c) for c in categories]
    form = rng.choice(s.settings.get("forms", ["most"]))
    values = rng.sample(list(s.params["value"].values()), len(categories))
    shown = list(values)
    options: list[int | str] = list(categories)
    target = ""
    words: dict[str, str] = {}
    if form == "most":
        answer: int | str = categories[values.index(max(values))]
    elif form == "least":
        answer = categories[values.index(min(values))]
    elif form == "how_many":
        target = rng.choice(categories)
        answer = values[categories.index(target)]
        options = sorted(values)
        words["name"] = s.label(target)
    else:
        i = rng.randrange(len(categories))
        shown[i] = max(0, values[i] + rng.choice([-2, -1, 1, 2]))
        if shown[i] == values[i]:
            shown[i] += 1
        answer = categories[i]
        words["tally"] = ", ".join(f"{c} {v}" for c, v in zip(names, values, strict=True))
    operands: dict[str, int | str] = {
        "title": s.label(data["title"]),
        "categories": " ".join(names),
        "values": " ".join(str(v) for v in shown),
        "counted": " ".join(str(v) for v in values),
        "ask": form,
        "target": target,
    }
    return make_task(s, level, operands, answer, s.template(form), s.options(options), words)
