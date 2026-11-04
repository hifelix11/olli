# backend

Python 3.12+, FastAPI, uv. Die gesamte Logik lebt hier.

```bash
uv sync
uv run uvicorn app.main:app --reload   # http://127.0.0.1:8000/health
uv run pytest
uv run ruff check . && uv run ruff format .
```

| Modul | Aufgabe |
| --- | --- |
| `app/domain/graph/` | Kompetenzgraph laden, Voraussetzungen und Zyklen prüfen, Tiefe |
| `app/domain/generators/` | Generator-Specs laden, Aufgaben erzeugen. Pro `kind` ein Modul |
| `app/domain/tracing/` | Bayesian Knowledge Tracing, Lernstand pro Kompetenz |
| `app/domain/selection/` | Nächste Kompetenz wählen, Schwierigkeit, Zurück zu den Grundlagen |
| `app/domain/tutor.py` | Übungsschleife: wählen, erzeugen, prüfen, aktualisieren. Noch ohne Datenbank |
| `app/domain/analysis/` | Fehlermuster erkennen (später) |
| `app/domain/language/` | LLM-Aufrufe, strikt gerahmt |
| `app/api/` | Routen |
| `app/db/` | Modelle, Migrationen |
