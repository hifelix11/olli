# generators

Pro Kompetenz eine Generator-Spezifikation als YAML. Die Logik liegt im Backend unter `app/domain/generators/`, pro `kind` ein Modul. Hier stehen nur Parameter.

| Feld | Bedeutung |
| --- | --- |
| `id` | stabil, gleich der Kompetenz-ID, wenn es nur einen Generator gibt |
| `competency` | Kompetenz-ID aus `competencies.yaml` |
| `kind` | Backend-Implementierung: `addition` (a + b = ?) oder `missing_addend` (a + ? = target) |
| `params` | Wertebereiche der Operanden als `{ min, max }` |
| `constraints` | Bedingungen an die Aufgabe, bei `addition`: `sum_min`, `sum_max` |
| `levels` | Überschreibungen für `easy` und `hard`, je mit `params` und `constraints`. `medium` ist die Basis. |
| `answer` | `free_input` oder `choice` (beeinflusst p_guess) |
| `representations` | erlaubte Darstellungen |

Noch ohne Generator: `count_to_20` (braucht eine Darstellung mit Mengen) und `add_within_20_no_carry` (braucht eine Bedingung "kein Übertrag").

Ziel für Klasse 1: etwa 30 Generatoren.
