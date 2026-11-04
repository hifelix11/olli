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
| `app/api/routes.py` | Routen, siehe unten |
| `app/db/` | Tabellen (`models.py`), Session, Repository für den Lernstand |
| `app/settings.py` | `DATABASE_URL`, CORS. Liest `.env` |
| `app/content.py` | Lädt Graph und Generatoren einmal beim ersten Zugriff |

## Routen

| Route | Zweck |
| --- | --- |
| `POST /children` `{name}` | Kind anlegen, liefert `id` |
| `GET /children/{id}/next-task` | Nächste Aufgabe ohne Lösung. `null`, wenn alles sitzt |
| `POST /children/{id}/answers` `{task_id, answer}` | Prüft, speichert den Versuch, aktualisiert den Lernstand. Liefert `correct`, Lösung, `p_known`, `backtracked_to` |
| `GET /children/{id}/mastery` | Alle Kompetenzen mit `p_known` und Status `mastered`, `in_progress`, `not_started` |

Interaktive Doku unter http://127.0.0.1:8000/docs.

## Datenbank

Tabellen werden beim Start mit `create_all` angelegt (noch keine Migrationen). `children`, `tasks` (ausgegebene Aufgaben mit Lösung), `attempts` (jede Antwort, unveränderlich), `mastery` (nur geübte Kompetenzen).

Die Tests laufen gegen SQLite im Speicher, die App gegen Postgres. Das Schema ist einfach genug, dass beide gleich funktionieren.
