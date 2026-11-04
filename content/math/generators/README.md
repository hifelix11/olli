# generators

Pro Kompetenz eine Generator-Spezifikation als YAML. Die Logik liegt im Backend unter `app/domain/generators/`, pro `kind` ein Modul. Hier stehen nur Parameter.

| Feld | Bedeutung |
| --- | --- |
| `id` | stabil, gleich der Kompetenz-ID, wenn es nur einen Generator gibt |
| `competency` | Kompetenz-ID aus `competencies.yaml` |
| `kind` | Backend-Implementierung, siehe Tabelle unten |
| `params` | Wertebereiche als `{ min, max }`, Namen je nach `kind` |
| `constraints` | Bedingungen an die Aufgabe, je nach `kind` |
| `settings` | Weitere Einstellungen je nach `kind`, z. B. `forms`, `relation`, `directions` |
| `variants` | Liste von Überschreibungen; pro Aufgabe wird eine zufällig gewählt |
| `levels` | Überschreibungen für `easy` und `hard`, je mit `params`, `constraints`, `settings`. `medium` ist die Basis. |
| `prompt` | Eigener Aufgabentext mit Platzhaltern für die Operanden, sonst Standard des `kind` |
| `answer` | `free_input` oder `choice`. Muss zum `kind` passen. |
| `representations` | erlaubte Darstellungen: plain, twenty_field, number_line, dice, fingers, scattered, tally |

Arten (`kind`):

| kind | Aufgabe | params | constraints / settings |
| --- | --- | --- | --- |
| `addition` | a + b = ? | a, b | sum_min, sum_max, no_carry, carry |
| `subtraction` | a − b = ? | a, b | result_min, result_max, no_borrow, borrow |
| `missing_number` | eine Zahl in a + b = c fehlt | a, target | settings.forms: a+_=c, _+b=c, c-_=a, _-b=a |
| `sequence_gap` | Zahlenfolge mit Lücke | start, step | settings: length, min_value, max_value, directions, gap |
| `count` | Wie viele? Darstellung zeigt n Dinge | n | |
| `number_word` | Zahlwort → Zahl | n | |
| `compare` | <, > oder = (choice) | a, b | |
| `even_odd` | gerade oder ungerade (choice) | n | |
| `related_fact` | Tausch-, Umkehr- oder Nachbaraufgabe | a, b | sum_max; settings.relation |
| `double_half` | Verdoppeln oder Halbieren | n | |
| `check_equation` | Stimmt das? (choice) | a, b | sum_max, result_min; settings.operations |
| `chance` | sicher, möglich, unmöglich (choice) | red, blue | |
| `compare_chances` | Welches Säckchen? (choice) | total, red_a, red_b | |

Stand: 32 von 68 Kompetenzen haben einen Generator. Ohne Generator sind alle Kompetenzen, die Bilder, Szenen, Texte oder Material brauchen: Rechengeschichten, Textaufgaben, Formen, Lagebegriffe, Uhr, Geld, Tabellen. Die kommen mit den passenden Darstellungen.
