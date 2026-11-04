"""kind: number_word. German number word in, digits out."""

import random

from app.domain.generators.models import GeneratorSpec, Task, choose, make_task

WORDS = [
    "null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn",
    "elf", "zwölf", "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn",
    "neunzehn", "zwanzig",
]  # fmt: skip
PROMPT = "Schreibe als Zahl: {word}"


def generate(spec: GeneratorSpec, level: str, rng: random.Random) -> Task:
    s = spec.resolve(level, rng)
    values = [n for n in s.params["n"].values() if 0 <= n < len(WORDS)]
    n = choose(values, spec, level, rng)
    return make_task(s, level, {"word": WORDS[n]}, n, PROMPT)
