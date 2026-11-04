# curricula

Mapping pro Bundesland: Kompetenz → Lehrplanstelle, Klasse, Halbjahr. Kompetenzen selbst stehen in `content/`. Ein neues Bundesland ist eine neue Mapping-Datei, keine neuen Aufgaben.

Dateiname: `<land>/<fach>-<klasse>.yaml`, z. B. `de-by/math-1.yaml`.

Aufbau: pro Teilbereich des Lehrplans (`ref`) die nummerierten Kompetenzerwartungen (`bullets`) in Kurzform mit den Kompetenz-IDs, die sie abdecken. `grade_2` nennt den Anteil, der erst später drankommt, `not_in_app` den Anteil, den die App nicht abdeckt. So bleibt sichtbar, was vom Lehrplan fehlt.

Quellen:

- Bayern: [LehrplanPLUS](https://www.lehrplanplus.bayern.de/)
- Übergreifend: KMK-Bildungsstandards Mathematik Primarbereich (Ende Klasse 4)
