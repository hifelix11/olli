# generators

Pro Kompetenz eine Generator-Spezifikation als YAML. Die Logik (Zahlen ziehen, Lösung berechnen) liegt im Backend unter `app/domain/selection/` oder einem eigenen Modul. Hier stehen nur Parameter.

Vorschlag für das Format, siehe `add_within_20_with_carry.yaml`:

| Feld | Bedeutung |
| --- | --- |
| `id` | stabil, gleich der Kompetenz-ID, wenn es nur einen Generator gibt |
| `competency` | Kompetenz-ID aus `competencies.yaml` |
| `kind` | Backend-Implementierung, z. B. `addition` |
| `params` | Wertebereiche der Operanden |
| `constraints` | Bedingungen an die Aufgabe, z. B. Summe über 10 |
| `levels` | Überschreibungen pro Schwierigkeit |
| `answer` | `free_input` oder `choice` (beeinflusst p_guess) |
| `representations` | erlaubte Darstellungen |

Ziel für Klasse 1: etwa 30 Generatoren.
