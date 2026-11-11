# generators

Pro Kompetenz eine Generator-Spezifikation als YAML. Die Logik liegt im Backend unter `app/domain/generators/`, pro `kind` ein Modul. Hier stehen die Parameter und alle Texte. Im Python-Code steht kein Text, den ein Kind sieht.

| Feld | Bedeutung |
| --- | --- |
| `id` | stabil, gleich der Kompetenz-ID, wenn es nur einen Generator gibt |
| `competency` | Kompetenz-ID aus `competencies.yaml` |
| `kind` | Backend-Implementierung, siehe Tabelle unten |
| `params` | Wertebereiche als `{ min, max }`, Namen je nach `kind` |
| `constraints` | Bedingungen an die Aufgabe, je nach `kind` |
| `settings` | Weitere Einstellungen je nach `kind`, z. B. `forms`, `relation`, `directions`. Keine Texte, nur IDs. |
| `variants` | Liste von Überschreibungen; pro Aufgabe wird eine zufällig gewählt |
| `levels` | Überschreibungen für `easy` und `hard`, je mit `params`, `constraints`, `settings`, `prompts`, `labels`. `medium` ist die Basis. |
| `prompt` | Aufgabentext mit Platzhaltern, für Arten mit einer Form |
| `prompts` | ein Aufgabentext pro Form, z. B. `most`, `least` |
| `labels` | Text für jede ID, die das Kind sieht |
| `answer` | `free_input` oder `choice`. Muss zum `kind` passen. |
| `representations` | erlaubte Darstellungen, siehe Tabelle unten. `plain` ist nur Text. |

## Texte

Der Code vergleicht und speichert Werte, das Kind sieht Texte. Deshalb sind Antworten und Optionen IDs (`even`, `yes`, `circle`) oder Zahlen, nie deutsche Wörter. `attempts` speichert den Wert. So bleibt eine Antwort gleich, auch wenn der Text sich ändert oder eine Sprache dazukommt.

- **IDs** sind `snake_case`. Jede ID, die das Kind sieht, braucht ein Label. Fehlt eins, schlagen die Tests fehl.
- **Zahlen, Buchstaben und Zeichen** wie `5`, `A`, `<`, `15 cm`, `3 + 4` brauchen kein Label. Sie erscheinen, wie sie sind.
- **Platzhalter** in `{}` füllt der Generator: Operanden wie `{a}` und Wörter, die er aus Labels baut, wie `{route}`. Welche es gibt, steht in der Tabelle.
- **Einzahl und Mehrzahl:** Ein Label kann `{ one: ..., other: ... }` sein. Der Generator wählt nach der Anzahl und setzt sie als `{n}` ein, z. B. `hours: { one: "{n} Stunde", other: "{n} Stunden" }`.
- **`yes` und `no` in Anführungszeichen:** YAML liest sie sonst als Wahrheitswerte. Das Backend lehnt das ab.
- **Items** (`item_choice`) haben ihren `prompt` direkt im Item. Optionen sind IDs mit Labels aus `labels`. Sätze, die nur ein Item braucht, stehen als Zuordnung ID → Text direkt in `options`.

Kommt eine Sprache dazu, bleibt Deutsch hier die Quelle. Übersetzt werden nur die Felder `prompt`, `prompts` und `labels`.

Arten (`kind`):

| kind | Aufgabe | params | constraints / settings | Texte |
| --- | --- | --- | --- | --- |
| `addition` | a + b = ? | a, b | sum_min, sum_max, no_carry, carry | prompt |
| `subtraction` | a − b = ? | a, b | result_min, result_max, no_borrow, borrow | prompt |
| `missing_number` | eine Zahl in a + b = c fehlt | a, target | settings.forms: a+_=c, _+b=c, c-_=a, _-b=a | prompts pro Form |
| `sequence_gap` | Zahlenfolge mit Lücke | start, step | settings: length, min_value, max_value, directions, gap | prompt mit {sequence} |
| `count` | Wie viele? Darstellung zeigt n Dinge | n | | prompt |
| `number_word` | Zahlwort → Zahl | n | | prompt mit {word}; labels: Zahlwörter, Schlüssel ist die Zahl |
| `compare` | <, > oder = (choice) | a, b | | prompt |
| `even_odd` | gerade oder ungerade (choice) | n | | prompt; labels even, odd |
| `related_fact` | Tausch-, Umkehr- oder Nachbaraufgabe | a, b | sum_max; settings.relation | prompt mit {a}, {b}, {c} = a + b, {d} = a + 1 |
| `double_half` | Verdoppeln oder Halbieren | n | | prompts double, half |
| `check_equation` | Stimmt das? (choice) | a, b | sum_max, result_min; settings.operations | prompt; labels correct, incorrect |
| `chance` | sicher, möglich, unmöglich (choice) | red, blue | | prompt mit {color}; labels certain, possible, impossible, red, blue |
| `compare_chances` | Welches Säckchen? (choice) | total, red_a, red_b | | prompt; Antwort A oder B |
| `item_choice` | feste Frage aus `settings.items` (prompt, answer, options), Platzhalter aus params (choice) | beliebig | settings.options als Standard | Items; labels für die Options-IDs |
| `word_problem` | Satz aus `settings.items` mit {a}, {b} und `op` (+, −, ×), Lösung gerechnet | a, b | sum_max, result_min, product_max | Items |
| `picture_equation` | Plättchen kommen dazu oder weg: Welche Aufgabe passt? (choice) | a, b | sum_max, result_min; settings.operations | prompt mit {action}; labels add, remove (Einzahl, Mehrzahl) |
| `plus_minus` | Plus oder Minus, pro Aufgabe gewählt | a, b | wie addition und subtraction; settings.operations | prompts "+", "−" |
| `clock` | Wie spät ist es? Volle und halbe Stunden (choice) | hour | settings.minutes | prompt; labels full, half mit {hour}, {next_hour}. Antwort wie `2:30` |
| `time_span` | Von 9 bis 12 Uhr: wie viele Stunden? 3 Stunden später? | start, hours | settings.forms, max_hour | prompts duration, later mit {span}; label hours (Einzahl, Mehrzahl) |
| `cycle_neighbour` | Was kommt nach Montag? (choice) | | settings.cycles (items, prompts after und before), directions | prompts mit {name}; labels für alle items |
| `money_amount` | Wie viel Geld ist das? | count | total_max; settings.values, unit | prompt |
| `money_exchange` | 10 € in 2-€-Münzen: wie viele? | | amount_max; settings.pieces (value, type) | prompt mit {name}; labels für die types |
| `compare_lengths` | Welcher Stab ist länger? (choice) | a, b | settings.ask | prompts longer, shorter; label equal |
| `measure` | Wie viele Büroklammern (Zentimeter) lang ist der Stab? | n | | prompt mit {unit}; label unit |
| `compare_quantities` | Was ist mehr, 5 € oder 12 €? (choice) | a, b | settings.ask | prompts more, less; label quantity mit {n}. Antwort ist die Zahl |
| `shape_name` | Welche Form ist das? (choice) | | settings.shapes, rotations | prompt; labels für die Formen |
| `shape_count` | Wie viele Ecken (Seiten) hat die Form? | | settings.shapes, ask, rotations | prompts corners, sides |
| `pattern_gap` | Muster aus Formen fortsetzen (choice) | unit, repeats | settings.symbols, gap | prompt; labels für die Formen |
| `grid_position` | Welcher Buchstabe steht links vom Käfer? (choice) | | settings.width, height, relations (left, right, above, below) | prompt mit {place}; labels für die relations |
| `grid_path` | 2 nach rechts, 1 nach oben: wo kommt der Käfer an? (choice) | legs, steps | settings.width, height | prompt mit {route}; labels right, left, up, down mit {n}, and |
| `symmetry` | Ist die Figur symmetrisch? (choice) | cells | settings.width, height | prompt; labels yes, no |
| `grid_copy` | Ist die Kopie richtig? (choice) | cells | settings.width, height | prompt; labels yes, no |
| `switch_representation` | Zahl aus Zwanzigerfeld, Zahlenstrahl, Zahlwort oder Zehner und Einer lesen | n | settings.forms | prompts pro Form, word mit {word}; labels: Zahlwörter |
| `estimate` | Wie viele sind es ungefähr? (choice) | n | settings.anchors | prompt |
| `bar_chart` | Säulendiagramm oder Tabelle lesen, falsche Säule finden (choice) | value | settings.sets (title, categories), forms | prompts pro Form, how_many mit {name}, wrong_bar mit {tally}; labels für titles und categories |

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
| `units`, `ruler` | n, unit (Label) | Stab mit Büroklammern, Stab über dem Lineal |
| `bar_chart`, `table` | title, categories (Labels), values | Säulendiagramm, Tabelle |

Nicht gezeichnet: `fingers` und `tally`, dort springt das nächste Bild in der Liste ein.

Stand: 66 von 68 Kompetenzen haben einen Generator. Ohne Generator bleiben `word_problems_to_10` und `word_problems_to_20`: Textaufgaben kommen geprüft aus `content/math/word_problems/`, nicht aus einem Generator. Die Item-Banken (`item_choice`) und Satzvorlagen (`word_problem`) sind handgeschriebene Inhalte im Status draft. Einige Kompetenzen prüft die App nur in einer Lesart: `build_charts` über die Säule, die nicht zu den gezählten Daten passt, `copy_shapes_on_grid` über den Vergleich von Vorlage und Kopie, `position_words` ohne vor und hinter, `solids` und `perspectives` in Worten statt in Bildern.
