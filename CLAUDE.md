# CLAUDE.md

Olli ist ein adaptiver Lernbegleiter für Grundschulkinder. Start: Mathematik, Jahrgangsstufe 1, Bayern. Der Kern ist Diagnose und Steuerung des Lernens (Knowledge Tracing), nicht das Generieren von Aufgaben. Das vollständige Konzept steht in `docs/konzept.md`.

## Working principles

Follow YAGNI principles. Prefer simple, minimal solutions and concise code. Use ASD-STE100-style language: short, clear, direct sentences. Keep output brief and focused. Alternate between IMPLEMENTATION and REFINEMENT: first implement the required solution, then make only changes that improve correctness, clarity, or maintainability without adding unnecessary complexity. Stop when no meaningful improvement remains.

## Repo-Struktur

```
backend/          Python + FastAPI. Gesamte Logik.
  app/main.py     FastAPI-App, legt Tabellen beim Start an
  app/settings.py DATABASE_URL, CORS aus .env
  app/content.py  Pfad zu content/, lädt Graph und Generatoren (gecacht)
  app/domain/     graph, generators, tracing, selection, analysis, language
  app/domain/tutor.py   Übungsschleife, verbindet die Module
  app/api/routes.py     children, next-task, answers, mastery
  app/db/         models (children, tasks, attempts, mastery), session, repository
  tests/
frontend/web/     Vite + React + TypeScript. Nur Anzeige und Antwort. Design-Tokens in src/index.css, Plan in der README.
content/          Fachinhalte als Daten, bundesland-unabhängig
  math/competencies.yaml   Kompetenzgraph
  math/generators/         Generator-Spezifikationen pro Kompetenz
  math/word_problems/      geprüfte Textaufgaben
curricula/        Mapping Kompetenz -> Lehrplanstelle, pro Bundesland
  de-by/math-1.yaml
docs/konzept.md   Konzept, Entscheidungen, offene Punkte
```

## Architektur-Regeln

Diese Regeln sind Entscheidungen. Nicht ohne Rücksprache ändern.

1. Kein Modell pro Kind trainieren. Der Lernstand ist eine Tabelle (`mastery`) plus Bayesian Knowledge Tracing.
2. Inhalte sind Daten in `content/`, nicht Code. Generator-Logik liegt im Backend, Generator-Parameter in YAML.
3. Kompetenzen sind universell. Lehrpläne sind Mappings in `curricula/`. Neues Bundesland = neue Mapping-Datei, keine neuen Aufgaben.
4. Logik komplett im Backend. Das Frontend zeigt an und sendet Antworten.
5. Nur FastAPI redet mit der Datenbank. Das Frontend spricht nie direkt mit Supabase. Grund: Portabilität zu Hetzner und Keycloak.
6. LLM strikt gerahmt: Erklärungen, Dialog mit der Figur, Sprachstufung, Zusammenfassungen. Nie frei chatten. Textaufgaben werden vorab generiert, geprüft und in den Pool gelegt. Nie live vor dem Kind.
7. `attempts` sind rohe, unveränderliche Ereignisse. Nie überschreiben, nie löschen, außer bei DSGVO-Löschung eines Profils.
8. Darstellung ist vom Generator getrennt. Dieselbe Aufgabe kann als Rechnung, Zwanzigerfeld oder Szene erscheinen.
9. Kinder sind Profile unter dem Elternkonto, ohne eigenes Login. Elternbereich per PIN.

## Konventionen

- Sprache: Code, Identifier und Commit-Messages auf Englisch. Doku, Inhalte und UI-Texte auf Deutsch.
- Schulbegriffe wie im Lehrplan: Jahrgangsstufe, nicht Klasse. Klasse nur für die Lerngruppe (`classes`).
- Python 3.12+, uv, FastAPI, Pydantic v2, ruff, pytest. Alles typisiert.
- TypeScript strict. Keine Logik im Frontend, die ins Backend gehört. Keine UI-Bibliothek, Styles in `index.css` mit den Tokens aus `frontend/web/README.md`.
- UI-Texte kurz, Sentence case, Du-Form für Kinder, Sie-frei für Eltern. Olli spricht in der ersten Person.
- IDs in YAML sind `snake_case` und stabil. Nie umbenennen, `attempts` referenzieren sie.
- Fachliche Zerlegungen (Kompetenzen, Voraussetzungen) sind Vorschläge, bis eine Didaktikerin sie geprüft hat. Status `draft` bleibt, bis das passiert ist.
- Kinderdaten: Datensparsamkeit. Keine Klarnamen in Logs oder LLM-Prompts.

## Befehle

```bash
cd backend && uv sync                        # Abhängigkeiten
cd backend && uv run uvicorn app.main:app --reload
cd backend && uv run pytest
cd backend && uv run ruff check . && uv run ruff format .
cd frontend/web && npm run dev               # sobald angelegt
supabase start                               # lokale Datenbank
```

## Datenmodell

| Bereich | Tabellen |
| --- | --- |
| Inhalt | subjects, competencies, prerequisites, generators, representations, word_problems |
| Curricula | states, curricula, curriculum_units, competency_mappings |
| Nutzer | children, guardians, teachers, classes |
| Lernen | attempts, mastery, sessions |

## Domänenbegriffe

- **Kompetenz (competency):** eine übbare Fähigkeit, feiner als der Lehrplan. Hat einen Bereich (`area`): numbers_operations, space_shape, quantities_measurement, data_chance.
- **Voraussetzung (prerequisite):** Kante im Graph. Wird nur geübt, wenn die Vorgänger sitzen.
- **Generator:** Vorlage mit Parametern, liefert korrekte Aufgaben mit bekannter Lösung.
- **Darstellung (representation):** wie eine Aufgabe gezeigt wird. Start: `plain`, `twenty_field`.
- **Textaufgabe (word problem):** Generator liefert Zahlen, LLM kleidet sie in eine Geschichte. Vorab geprüft.
- **Sprachstufe (language level):** gleiche Mathe, mehr oder weniger Text.
- **Versuch (attempt):** eine Antwort als Ereignis mit Zeit, Hilfebedarf, Darstellung.
- **Lernstand (mastery):** Wahrscheinlichkeit pro Kind und Kompetenz.
- **BKT-Parameter:** p_init (Vorwissen), p_learn (Lernrate), p_slip (Verhauen), p_guess (Raten).

## Lernlogik, Stand Durchstich

- Lernstand: `LearnerState.mastery` pro Kompetenz, Start bei `p_init`, Update per BKT in `tracing/bkt.py`.
- Auswahl in `selection/select.py`: nicht gemeistert, alle Voraussetzungen ab `MASTERED` (0,95), geringste Tiefe zuerst, dann die mit dem höchsten Lernstand.
- Schwierigkeit aus dem Lernstand: unter 0,4 `easy`, unter 0,75 `medium`, sonst `hard`.
- Zurück zu den Grundlagen: nach `BACKTRACK_AFTER` (3) Fehlern in Folge sinkt die schwächste direkte Voraussetzung auf `DOUBT` (0,3) und wird geübt, bis sie wieder sitzt.
- Generator-Kinds stehen in `content/math/generators/README.md`. Eine Spec pro Kompetenz, 32 von 68 haben eine. Kompetenzen ohne Generator werden nie gewählt und blockieren ihre Nachfolger nicht (`practicable` in `select_next`). Die Elternkarte zeigt sie blass.
- Aufgaben mit Auswahl (`options`) heben die Rate-Rate auf mindestens 1 / Anzahl Optionen.
- Der Demo-Fall steht in `tests/test_tutor.py` und über HTTP in `tests/test_api.py`.
- API: Lösung bleibt im Backend (`tasks.payload`). Eine Aufgabe kann nur einmal beantwortet werden. `mastery` hat nur Zeilen für geübte Kompetenzen, der Rest gilt als `not_started`.
- Tests laufen gegen SQLite im Speicher (Dependency-Override von `get_session`), die App gegen Postgres.

## Prototyp 0.1

Ziel der Demo: Das System merkt, wo ein Kind hängt, und geht zurück. Das ist der Kern, nicht die Spielwelt. Zuerst ein Durchstich: ein Generator, Knowledge Tracing, Auswahl. Dann breiter.

Nicht im Scope: Textaufgaben, Sprachstufen, Fehlermuster-Analyse, Spielwelt, Lehrkraft-Bereich, native App.
