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
| `representations` | erlaubte Darstellungen, siehe Tabelle unten. `plain` ist nur Text. |

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
| `item_choice` | feste Frage aus `settings.items` (prompt, answer, options), Platzhalter aus params (choice) | beliebig | settings.options als Standard |
| `word_problem` | Satz aus `settings.items` mit {a}, {b} und `op` (+, −, ×), Lösung gerechnet | a, b | sum_max, result_min, product_max |
| `picture_equation` | Plättchen kommen dazu oder weg: Welche Aufgabe passt? (choice) | a, b | sum_max, result_min; settings.operations |
| `plus_minus` | Plus oder Minus, pro Aufgabe gewählt | a, b | wie addition und subtraction; settings.operations |
| `clock` | Wie spät ist es? Volle und halbe Stunden (choice) | hour | settings.minutes |
| `time_span` | Von 9 bis 12 Uhr: wie viele Stunden? 3 Stunden später? | start, hours | settings.forms, max_hour |
| `cycle_neighbour` | Was kommt nach Montag? (choice) | | settings.cycles (items, after, before), directions |
| `money_amount` | Wie viel Geld ist das? | count | total_max; settings.values, unit |
| `money_exchange` | 10 € in 2-€-Münzen: wie viele? | | amount_max; settings.pieces |
| `compare_lengths` | Welcher Stab ist länger? (choice) | a, b | settings.ask |
| `measure` | Wie viele Büroklammern (Zentimeter) lang ist der Stab? | n | settings.unit |
| `compare_quantities` | Was ist mehr, 5 € oder 12 €? (choice) | a, b | settings.unit, more, less, ask |
| `shape_name` | Welche Form ist das? (choice) | | settings.shapes, rotations |
| `shape_count` | Wie viele Ecken (Seiten) hat die Form? | | settings.shapes, ask, rotations |
| `pattern_gap` | Muster aus Formen fortsetzen (choice) | unit, repeats | settings.symbols, gap |
| `grid_position` | Welcher Buchstabe steht links vom Käfer? (choice) | | settings.width, height, relations |
| `grid_path` | 2 nach rechts, 1 nach oben: wo kommt der Käfer an? (choice) | legs, steps | settings.width, height |
| `symmetry` | Ist die Figur symmetrisch? (choice) | cells | settings.width, height |
| `grid_copy` | Ist die Kopie richtig? (choice) | cells | settings.width, height |
| `switch_representation` | Zahl aus Zwanzigerfeld, Zahlenstrahl, Zahlwort oder Zehner und Einer lesen | n | settings.forms |
| `estimate` | Wie viele sind es ungefähr? (choice) | n | settings.anchors |
| `bar_chart` | Säulendiagramm oder Tabelle lesen, falsche Säule finden (choice) | value | settings.sets, forms |

Darstellungen (`representations`) und die Operanden, die das Frontend dafür liest. Listen stehen als Text mit Leerzeichen, Zellen als `x,y` mit y nach unten:

| Darstellung | liest | zeigt |
| --- | --- | --- |
| `plain` | | nur den Text |
| `twenty_field` | je nach kind, siehe `counters.ts` | Zwanzigerfeld mit Plättchen |
| `dice` | n | Würfelbild |
| `scattered` | n | ungeordnete Plättchen |
| `number_line` | n | Zahlenstrahl 0 bis 20 mit Pfeil |
| `shapes` | shapes (ids, `_` = Lücke), rotation | Reihe aus Formen |
| `grid` | width, height, cells, copy, axis, start, marks | Gitter mit Figur, Spiegelachse, Käfer, Buchstaben |
| `clock`, `digital_clock` | hour, minute | Analoguhr, Digitaluhr |
| `money` | coins, unit | Münzen und Scheine |
| `lengths` | a, b | zwei Stäbe A und B |
| `units`, `ruler` | n, unit | Stab mit Büroklammern, Stab über dem Lineal |
| `bar_chart`, `table` | title, categories, values | Säulendiagramm, Tabelle |

Nicht gezeichnet: `fingers` und `tally`, dort springt das nächste Bild in der Liste ein.

Stand: 66 von 68 Kompetenzen haben einen Generator. Ohne Generator bleiben `word_problems_to_10` und `word_problems_to_20`: Textaufgaben kommen geprüft aus `content/math/word_problems/`, nicht aus einem Generator. Die Item-Banken (`item_choice`) und Satzvorlagen (`word_problem`) sind handgeschriebene Inhalte im Status draft. Einige Kompetenzen prüft die App nur in einer Lesart: `build_charts` über die Säule, die nicht zu den gezählten Daten passt, `copy_shapes_on_grid` über den Vergleich von Vorlage und Kopie, `position_words` ohne vor und hinter, `solids` und `perspectives` in Worten statt in Bildern.
