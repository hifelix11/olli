# frontend/web

Web-App als PWA: Kinderbereich (Aufgaben, Olli, Zwanzigerfeld), Elternbereich (PIN, Lernstand als Karte). Nur Anzeige und Antwort. Alle Logik liegt im Backend.

Vite + React 19 + TypeScript, Linter: oxlint. Keine weiteren Abhängigkeiten.

```bash
npm install
npm run dev       # http://localhost:5173, Backend muss auf 8000 laufen
npm run build     # tsc + vite build
npm run lint
```

Backend-Adresse über `VITE_API_URL`, Standard `http://127.0.0.1:8000`.

## Struktur

```
src/
  api/client.ts        Typen und die Aufrufe ans Backend
  representations/     Figure.tsx wählt das Bild zur Aufgabe, pick.ts die Darstellung; counters.ts (Aufgabe → Plättchen);
                       ein Bild pro Datei: TwentyField, Dice, Scattered, NumberLine, Shapes, Grid, Clock,
                       DigitalClock, Money, Lengths, Units, Ruler, BarChart, Table
  child/               Practice (Sitzung), TaskView (Aufgabe), Keypad, Olli
  parent/ParentArea    PIN, Kinder anlegen, Jahresziel und Karte
  start/Start          Kind wählen
  storage.ts           Kinderliste im localStorage
  speech.ts            Vorlesen per Browser-Sprachausgabe
  index.css            Tokens und alle Styles
```

## Design

Das Kind sieht sein Matheheft, nicht eine App. Alles kommt aus dem Material der ersten Jahrgangsstufe: Karopapier, Füllertinte, rote und blaue Wendeplättchen im Zwanzigerfeld mit Lücke nach fünf.

| Token | Wert | Herkunft |
| --- | --- | --- |
| Papier | `#FCFBF7` | Heftseite |
| Karo | `#D7DFEA` | Lineatur des Rechenhefts |
| Tinte | `#1D2B50` | Füllertinte |
| Rot, Blau | `#E0442F`, `#2E62D9` | Wendeplättchen |
| Grün, Gelb, Grau | `#2F9E5B`, `#F2B531`, `#C3C7CF` | nur die Elternkarte: sitzt, in Arbeit, kommt noch |

Schrift: Andika (SIL), eine Familie in Regular und Bold. Entworfen für Leseanfänger: einstöckiges a, klar unterscheidbare 1, l und I. Zahlen in der Aufgabe 64 px, Frage 28 px, Tastatur 32 px.

Regeln:

- Das Zwanzigerfeld ist das Merkzeichen. Alles andere bleibt still: keine Schatten, keine Karten, keine Dekoration.
- Kein Text, den ein Erstklässler nicht braucht. Jede Frage lässt sich vorlesen.
- Eine Bewegung: beim Prüfen füllen sich die leeren Plättchen.
- Eine Sitzung hat 10 Aufgaben, sichtbar als Kästchen oben rechts. Danach ist Schluss.
- Ein neues Kind bekommt zuerst den Standortcheck. Olli sagt das im Kopf der Seite und tröstet bei Fehlern: "Das üben wir später."
- Tastatur groß, Eingabe per Zahlenblock oder große Auswahlknöpfe. Auf dem Rechner geht auch die Tastatur.

Darstellungen: Das Backend nennt pro Aufgabe die erlaubten Darstellungen, `Figure` zeichnet die erste, die das Frontend kann. Sind es mehrere (etwa `bar_chart` und `table`), entscheidet die Aufgaben-ID, damit dieselbe Aufgabe ihr Bild behält. `plain` ist kein Bild. Gebaut sind `twenty_field`, `dice`, `scattered`, `number_line`, `shapes`, `grid`, `clock`, `digital_clock`, `money`, `lengths`, `units`, `ruler`, `bar_chart` und `table`. Nicht gezeichnet: `fingers` (die Würfelbilder springen ein) und `tally` (Zählaufgaben fallen auf das Zwanzigerfeld zurück). Alle Bilder sind Inline-SVG oder HTML, Gitter und Längen rechnen in Kästchen von 28 px wie das Papier. Die Operanden, die jedes Bild liest, stehen in `content/math/generators/README.md`.

Die Eltern-PIN ist `1234`, fest im Code, bis es Elternkonten gibt.
