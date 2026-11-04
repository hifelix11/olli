# content

Fachinhalte als Daten, bundesland-unabhängig. Pro Fach ein Ordner.

| Datei / Ordner | Inhalt |
| --- | --- |
| `math/competencies.yaml` | Kompetenzgraph: Fähigkeiten mit Voraussetzungen, Bereich und BKT-Startparametern. Klasse 1 vollständig (68 Kompetenzen) |
| `math/generators/` | Pro Kompetenz eine Generator-Spezifikation (Parameter, Schwierigkeit, Antworttyp) |
| `math/word_problems/` | Geprüfte Textaufgaben nach Sprachstufe. Nie live generiert. |

Regeln:

- IDs sind `snake_case` und stabil. Nie umbenennen, `attempts` referenzieren sie.
- Status `draft`, bis eine Didaktikerin die Zerlegung geprüft hat.
- Lehrplan-Bezug steht nicht hier, sondern in `curricula/`. Ein Test prüft, dass jede Kompetenz dort vorkommt.
- Nur aufnehmen, was die App diagnostizieren und üben kann. Handelnde Lehrplan-Anteile stehen in `curricula/` unter `not_in_app`.
