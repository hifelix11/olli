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
| `app/api/auth.py` | Login über Supabase Auth, Token-Prüfung, siehe Anmeldung |
| `app/db/` | Tabellen (`models.py`), Session, Repository für den Lernstand |
| `app/settings.py` | `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, CORS. Liest `.env` |
| `app/content.py` | Lädt Graph und Generatoren einmal beim ersten Zugriff |

## Routen

Alle Routen unter `/children` brauchen `Authorization: Bearer <access_token>`. Ein Elternteil sieht nur eigene Kinder. Ein fremdes Kind ist 404.

| Route | Zweck |
| --- | --- |
| `POST /auth/signup` `{email, password}` | Konto anlegen. Liefert Tokens oder `null`, wenn erst die E-Mail bestätigt werden muss |
| `POST /auth/login` `{email, password}` | Liefert `access_token`, `refresh_token` |
| `POST /auth/refresh` `{refresh_token}` | Neue Tokens. 401, wenn die Anmeldung abgelaufen ist |
| `GET /children` | Kinder des Elternteils |
| `POST /children` `{name}` | Kind anlegen, liefert `id` |
| `GET /children/{id}/next-task` | Nächste Aufgabe ohne Lösung. `null`, wenn alles sitzt |
| `POST /children/{id}/answers` `{task_id, answer}` | Prüft, speichert den Versuch, aktualisiert den Lernstand. Liefert `correct`, Lösung, `p_known`, `backtracked_to` |
| `GET /children/{id}/mastery` | Alle Kompetenzen mit `p_known`, Status `mastered`, `in_progress`, `not_started` und `practicable` (hat einen Generator) |

Interaktive Doku unter http://127.0.0.1:8000/docs.

## Datenbank

Tabellen werden beim Start mit `create_all` angelegt (noch keine Migrationen). `create_all` legt fehlende Tabellen an, ändert aber keine bestehenden. Eine neue Spalte braucht deshalb lokal einen Neuanfang der Tabellen. `guardians` (Elternkonten, ID aus Supabase Auth, keine E-Mail), `children`, `tasks` (ausgegebene Aufgaben mit Lösung), `attempts` (jede Antwort, unveränderlich), `mastery` (nur geübte Kompetenzen).

Die Tests laufen gegen SQLite im Speicher, die App gegen Postgres. Das Schema ist einfach genug, dass beide gleich funktionieren.

Bekannte Lücke: Ein unbehandelter Fehler (500) trägt keine CORS-Header, der Browser meldet dann nur "Failed to fetch". Die Ursache steht im Server-Log.

## Anmeldung

Das Frontend spricht nie mit Supabase. FastAPI leitet Registrierung, Login und Refresh an Supabase Auth weiter (`SUPABASE_URL/auth/v1`, mit dem Publishable Key). Fehler behalten ihren Status, `detail` ist der Fehlercode von Supabase, etwa `invalid_credentials`. Das Frontend übersetzt ihn.

Die Tokens prüft FastAPI selbst: Signatur über die öffentlichen Schlüssel (`/auth/v1/.well-known/jwks.json`, ES256 oder RS256), Aussteller, Zielgruppe `authenticated`, Ablauf. `sub` ist die ID des Elternteils. Für Keycloak ändert sich nur `app/api/auth.py`.

Lokal sind E-Mail-Bestätigungen aus (`supabase/config.toml`). Mails landen in Mailpit unter http://127.0.0.1:54324.

## Umzug zu Supabase Cloud

1. Projekt in Frankfurt anlegen (`eu-central-1`). Neue Projekte signieren Tokens asymmetrisch, das passt ohne Änderung.
2. In `.env`: `DATABASE_URL` (Verbindung aus dem Dashboard, mit `sslmode=require`), `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`. Die Tabellen entstehen beim Start.
3. Im Dashboard unter Auth: Site URL auf die Adresse des Frontends, eigener SMTP-Server (der eingebaute schickt nur wenige Mails pro Stunde). E-Mail-Bestätigung ist in der Cloud an, das Frontend kann damit umgehen.
4. Daten, falls nötig: `pg_dump` von `public` sowie `auth.users` und `auth.identities`. Passwörter bleiben gültig. Alte Tokens nicht, alle melden sich einmal neu an.

Sobald echte Daten in der Cloud liegen, reicht `create_all` nicht mehr. Dann Alembic einrichten.
