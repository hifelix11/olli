# Olli

Adaptiver KI-Lernbegleiter für Grundschulkinder. Arbeitstitel.

Olli erkennt, wo ein Kind hängt, und entscheidet selbst, was als Nächstes dran ist. Der Kern ist Diagnose und Steuerung des Lernens (Knowledge Tracing), nicht das Generieren von Aufgaben. Kein ChatGPT im Kinderdesign.

**Status:** Konzeptphase. Prototyp 0.1 in Arbeit: Bayern, Mathematik, Jahrgangsstufe 1.

Das vollständige Konzept steht in [docs/konzept.md](docs/konzept.md).

## Was Olli anders macht

- **Diagnose statt Generierung.** Ein Lernstandsmodell pro Kind und Kompetenz entscheidet, ob es weitergeht, schwieriger wird oder zurück zu den Grundlagen geht.
- **Lehrplan als Graph.** Fähigkeiten mit Voraussetzungen, feiner zerlegt als der Lehrplan. Das ist das eigentliche Know-how.
- **Aufgaben aus Generatoren.** Pro Fähigkeit eine Vorlage mit Parametern, automatisch korrekt, getrennt von der Darstellung.
- **LLM nur für Sprache.** Erklärungen, Dialog mit der Figur, Textaufgaben. Strikt gerahmt, nie frei chattend.
- **Kurze Einheiten.** Das Produkt soll Zeit sparen, nicht verbrauchen.

## Aufbau des Repos

| Ordner | Inhalt |
| --- | --- |
| `backend/` | Python + FastAPI. Kompetenzgraph, Knowledge Tracing, Auswahl-Logik, Fehleranalyse, LLM-Schicht, API, Datenbank. Die gesamte Logik lebt hier. |
| `frontend/web/` | Vite + React + TypeScript als PWA. Kinderbereich, Elternbereich, Darstellungen der Aufgaben. Nur Anzeige und Antwort. |
| `content/` | Fachinhalte als Daten, pro Fach: Kompetenzgraph, Generatoren, geprüfte Textaufgaben. Bundesland-unabhängig. |
| `curricula/` | Mapping pro Bundesland: Kompetenz → Lehrplanstelle, Jahrgangsstufe, Halbjahr. Neues Bundesland = neue Datei. |
| `docs/` | Konzept und Entscheidungen. |

## Architektur

| Schicht | Aufgabe | Umsetzung |
| --- | --- | --- |
| Kompetenzgraph | Fähigkeiten mit Voraussetzungen | `content/math/competencies.yaml`, handkuratiert |
| Aufgabenpool | Generatoren plus Darstellungen plus geprüfte Textaufgaben | `content/math/generators/`, `content/math/word_problems/` |
| Lernstandsmodell | Pro Kind und Kompetenz eine Wahrscheinlichkeit, dass sie sitzt | Bayesian Knowledge Tracing, `backend/app/domain/tracing/` |
| Auswahl-Logik | Nächste Aufgabe: knapp über dem Können, Wiederholung, Grundlagen zuerst | `backend/app/domain/selection/` |
| Fehleranalyse | Typische Fehlermuster erkennen | `backend/app/domain/analysis/`, regelbasiert |
| LLM-Schicht | Erklärungen in Kindersprache, Dialog, Sprachstufung, Zusammenfassungen | `backend/app/domain/language/`, API-Aufrufe |

Kein Modell wird pro Kind trainiert. Das Mitlernen ist ein Lernstandsmodell in der Datenbank plus ein Algorithmus, der daraus die nächste Aufgabe wählt.

## Tech-Stack

| Bereich | Entscheidung |
| --- | --- |
| Backend | Python 3.12+, FastAPI, uv |
| Frontend | Vite + React + TypeScript, PWA |
| Spielwelt | PixiJS oder Phaser (später) |
| Datenbank | PostgreSQL über Supabase, lokal per Supabase CLI |
| Auth | Supabase Auth, Eltern-PIN als zusätzliche Sperre |
| Inhalte | YAML im Repo, beim Start in die Datenbank geladen |
| Hosting | Deutscher Anbieter (z. B. Hetzner), Kinderdaten und DSGVO |

Nur das Backend redet mit der Datenbank. Das Frontend spricht nie direkt mit Supabase. So bleibt es normales Postgres und ist jederzeit umziehbar.

## Prototyp 0.1

Ziel: Die Demo zeigt, dass das System merkt, wo ein Kind hängt, und zurückgeht.

Drin:

- Kompetenzgraph Mathe Jahrgangsstufe 1 Bayern
- Generatoren für etwa die Hälfte der Kompetenzen
- Zwei Darstellungen: nackte Rechnung und Zwanzigerfeld
- Knowledge Tracing, Auswahl-Logik, Zurück-zu-den-Grundlagen
- LLM nur für kurze Erklärungen nach einem Fehler
- Elternbereich mit PIN und Graph als Karte
- Figur als Maskottchen, das lobt und erklärt

Nicht drin: Textaufgaben, Sprachstufen, Fehlermuster-Analyse, Spielwelt, Lehrkraft-Bereich, native App.

## Loslegen

Voraussetzungen: Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 22+, Docker, [Supabase CLI](https://supabase.com/docs/guides/local-development).

```bash
# Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload
# http://127.0.0.1:8000/health

# Tests
uv run pytest

# Frontend, http://localhost:5173
cd frontend/web
npm install
npm run dev

# Datenbank (lokal)
supabase start
```

## Prinzipien

- Kompetenzen sind universell, Lehrpläne sind nur ein Mapping darauf.
- Logik komplett im Backend, Frontend nur Anzeige und Antwort.
- Jede Antwort eines Kindes ist ein rohes, dauerhaftes Ereignis (`attempts`). Das ist der Datenschatz für spätere Parameterschätzung.
- Darstellung einer Aufgabe ist vom Generator getrennt.
- Datensparsamkeit. Kinder sind Profile unter dem Elternkonto, ohne eigenes Login.
