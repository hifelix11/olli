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
| `app/domain/graph/` | Kompetenzgraph laden, Voraussetzungen prüfen |
| `app/domain/tracing/` | Bayesian Knowledge Tracing, Lernstand aktualisieren |
| `app/domain/selection/` | Nächste Aufgabe wählen, Spaced Repetition, Generatoren ausführen |
| `app/domain/analysis/` | Fehlermuster erkennen (später) |
| `app/domain/language/` | LLM-Aufrufe, strikt gerahmt |
| `app/api/` | Routen |
| `app/db/` | Modelle, Migrationen |
