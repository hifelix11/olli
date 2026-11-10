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

Anmeldung: Das Frontend schickt E-Mail und Passwort ans Backend, nie an Supabase. `api/client.ts` hängt das Token an jede Anfrage. Bei 401 holt es einmal neue Tokens und wiederholt die Anfrage. Klappt das nicht, endet die Anmeldung und der Login erscheint. Die Kinderliste kommt vom Backend. Abmelden geht im Elternbereich, hinter der PIN.

## Struktur

```
src/
  api/client.ts        Typen und die Aufrufe ans Backend
  representations/     Figure.tsx wählt das Bild zur Aufgabe, pick.ts die Darstellung; counters.ts (Aufgabe → Plättchen);
                       ein Bild pro Datei: TwentyField, Dice, Scattered, NumberLine, Shapes, Grid, Clock,
                       DigitalClock, Money, Lengths, Units, Ruler, BarChart, Table
  child/               Practice (Sitzung), TaskView (Aufgabe), Keypad, Olli, Stamp (Ende der Sitzung),
                       Sign und signs.ts (Zeichen der Kinder), Icon (Symbole statt Wörter)
  parent/ParentArea    PIN, Kinder anlegen, Jahresziel und Karte
  start/Login          Anmelden und Konto anlegen (Elternkonto)
  start/Start          Kind wählen
  storage.ts           Tokens des Elternkontos im localStorage
  speech.ts            Vorlesen per Browser-Sprachausgabe
  sound.ts             Zweiklang bei richtig, schaltet Ton und Sprache in Safari frei
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
- Zwei Bewegungen: beim Prüfen füllen sich die leeren Plättchen, am Ende fällt der Stempel ins Heft.
- Eine Sitzung hat 10 Aufgaben, sichtbar als Kästchen oben rechts. Danach ist Schluss, ohne "Noch eine Runde".
- Tastatur groß, Eingabe per Zahlenblock oder große Auswahlknöpfe. Auf dem Rechner geht auch die Tastatur.

## Ablauf für das Kind

Das Kind ist 6 und liest noch nicht. Was es verstehen muss, kommt als Stimme, Bild oder Symbol. Text ist für die Eltern. Olli spricht in der ersten Person und nie den Namen des Kindes aus, denn die Sprachausgabe des Browsers kann über einen Server laufen.

1. Start: Jedes Kind hat ein Zeichen wie an der Kita-Garderobe, die Eltern wählen es beim Anlegen. Das Tippen darauf schaltet Ton und Sprache frei.
2. Begrüßung: Olli sagt, was kommt. Das Kind tippt auf ▶.
3. Aufgabe: Olli liest sie vor, der Lautsprecher wiederholt sie. Im Kopf nur Olli mit Sprechblase, die Kästchen und das Haus.
4. Richtig: Zweiklang, Olli freut sich, nach 1,1 s geht es weiter.
5. Falsch: Bei freier Eingabe sagt Olli "Schau nochmal." und das Kind hat einen zweiten Versuch. Danach zeigt Olli die Lösung, weiter mit →. Bei Auswahl gleich die Lösung, ein zweiter Versuch wäre dort geraten.
6. Standortcheck: Er probiert absichtlich zu Schweres, deshalb kein richtig oder falsch. Olli sagt "Gemerkt!". Das Fragezeichen ("Weiß ich noch nicht") senkt das Raten, Olli sagt "Das üben wir später." Ist der Check vorbei, sagt Olli: "Jetzt weiß ich, was du kannst."
7. Zurück zu den Grundlagen: Vor der nächsten Aufgabe sagt Olli "Wir üben erst etwas, das dir dabei hilft." Das klingt nach Werkzeug, nicht nach Abstieg.
8. Ende: Nach 10 Aufgaben drückt Olli einen Stempel ins Heft. Blau mit Gesicht, rot mit Stern, wenn eine Kompetenz neu sitzt, darunter "Neu: …".

Das Zwanzigerfeld legt zeilenweise, obere Reihe zuerst: 8 + 5 zeigt die volle Zehn und 3 darunter. Gerade und ungerade legt es paarweise in Spalten, ein Plättchen ohne Partner heißt ungerade. Verdoppeln und Halbieren legt es gespiegelt, oben so viele wie unten.

Darstellungen: Das Backend nennt pro Aufgabe die erlaubten Darstellungen, `Figure` zeichnet die erste, die das Frontend kann. Sind es mehrere (etwa `bar_chart` und `table`), entscheidet die Aufgaben-ID, damit dieselbe Aufgabe ihr Bild behält. `plain` ist kein Bild. Gebaut sind `twenty_field`, `dice`, `scattered`, `number_line`, `shapes`, `grid`, `clock`, `digital_clock`, `money`, `lengths`, `units`, `ruler`, `bar_chart` und `table`. Nicht gezeichnet: `fingers` (die Würfelbilder springen ein) und `tally` (Zählaufgaben fallen auf das Zwanzigerfeld zurück). Alle Bilder sind Inline-SVG oder HTML, Gitter und Längen rechnen in Kästchen von 28 px wie das Papier. Die Operanden, die jedes Bild liest, stehen in `content/math/generators/README.md`.

Die Eltern-PIN ist `1234`, fest im Code, bis sie im Elternkonto liegt.
