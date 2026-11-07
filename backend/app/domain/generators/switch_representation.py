"""kind: switch_representation. The same number in another form: read it off.

params: n. settings.forms: subset of [twenty_field, number_line, word, tens_ones].
The task carries only the representation its form needs.
"""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task
from app.domain.generators.number_word import WORDS

PROMPTS = {
    "twenty_field": "Welche Zahl zeigt das Zwanzigerfeld?",
    "number_line": "Welche Zahl zeigt der Pfeil?",
    "word": "Schreibe als Zahl: {word}",
    "tens_ones": "Welche Zahl ist das? {tens} Zehner und {ones} Einer",
}
REPRESENTATIONS = {
    "twenty_field": ["twenty_field"],
    "number_line": ["number_line"],
    "word": ["plain"],
    "tens_ones": ["plain"],
}


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    form = rng.choice(s.settings.get("forms", list(PROMPTS)))
    lowest = 10 if form == "tens_ones" else 0
    values = [n for n in s.params["n"].values() if lowest <= n <= 20]
    n = choose(values, spec, level, rng)
    operands: dict[str, int | str] = {
        "n": n,
        "form": form,
        "word": WORDS[n],
        "tens": n // 10,
        "ones": n % 10,
    }
    task = make_task(s, level, operands, n, PROMPTS[form])
    return task.model_copy(update={"representations": REPRESENTATIONS[form]})
