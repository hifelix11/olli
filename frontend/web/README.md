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
                       Burst (Formen bei richtig), Sign und signs.ts (Zeichen der Kinder), Icon (Symbole statt Wörter)
  parent/ParentArea    PIN, Kinder anlegen, Jahresziel und Karte
  parent/PinPad        Punkte und Zahlenblock für die PIN
  parent/SignPicker    Zeichen für ein neues Kind wählen, auch im Onboarding
  start/Entry          Rahmen für Anmelden und Onboarding: Olli auf Rosa, daneben das Formular
  start/Login          Anmelden und Konto anlegen (Elternkonto)
  start/Onboarding     erster Start: Kind mit Zeichen anlegen, PIN wählen
  start/Start          Kind wählen
  route.ts             Adresse und Ansicht, ohne Router-Bibliothek
  storage.ts           Tokens des Elternkontos im localStorage
  speech.ts            Vorlesen per Browser-Sprachausgabe
  sound.ts             Zweiklang bei richtig, schaltet Ton und Sprache in Safari frei
  index.css            Tokens und alle Styles
```

## Design

Die Formenkiste. Ollis Welt besteht aus flachen Formen, wie sie ein Kind in der ersten Jahrgangsstufe in der Hand hat: Wendeplättchen, Würfel, Dreiecke. Olli ist ein Otter als runder Kiesel mit Gesicht. Einfach wie ein Spiel, aber ohne Spielkonsole: keine 3D-Knöpfe, kein Lernpfad, kein Grün als Hauptfarbe.

| Token | Wert | Rolle |
| --- | --- | --- |
| Kreide | `#F3F1F9` | Hintergrund |
| Tafel | `#FFFFFF` | Aufgabe, Tasten, Felder |
| Nacht | `#24204A` | Text, Knöpfe für Eltern |
| Rot, Blau | `#F24C3D`, `#2E5BF0` | Wendeplättchen, Fortschritt |
| Sonne | `#FFC83D` | alles, was das Kind antippt, um weiterzukommen; Ende der Sitzung |
| Rosa | `#FFB8D9` | Start, Anmelden, Ollis Sprechblase |
| Olli | `#F08A3C`, `#FFE6CC` | Fell, Schnauze |
| Grün | `#2FA562` | nur die Elternkarte: sitzt |

Schrift: Jost, eine Familie von 400 bis 800. Geometrisch wie die Druckschrift der Grundschule: einstöckiges a und g, einfache Striche. Zahlen in der Aufgabe 76 px (Telefon 54 px), Frage 28 px, Tastatur 34 px.

Regeln:

- Flach: keine Schatten, keine Verläufe. Formen sind rund, Knöpfe sind Pillen oder Kreise.
- Volle Farbe nur an den Rändern der Sitzung: Start rosa, Begrüßung blau, Ende gelb. Die Aufgabe selbst bleibt ruhig: weiße Tafel auf Kreide.
- Gelb heißt los: Play, Haken, Pfeil. Die Knöpfe für Eltern sind Nacht.
- Jeder Knopf gibt beim Drücken nach (Skalierung), Tasten werden dabei blau. Kinder erwarten auf jeden Tipp eine Antwort.
- Bewegung nur als Antwort: Olli hüpft bei richtig, Formen fliegen aus der Tafel, die Tafel wackelt beim zweiten Versuch, ein Plättchen ploppt in den Fortschritt, der Stempel fällt. `prefers-reduced-motion` schaltet alles ab.
- Olli sitzt auf der Kante der Tafel, die Sprechblase daneben. Olli und Tafel stehen als Gruppe in der Mitte. Antworten liegen unter der Tafel. Nur der Zahlenblock liegt quer rechts in einer festen Spalte: Unter der Tafel ist er zu hoch, und die Tafel springt nach der Antwort nicht.
- Kein Scrollen beim Üben, auch nicht auf dem Telefon.
- Kein Text, den ein Erstklässler nicht braucht. Jede Frage lässt sich vorlesen.
- Eine Sitzung hat 10 Aufgaben, sichtbar als zehn Plättchen oben, mit Lücke nach fünf. Danach ist Schluss, ohne "Noch eine Runde".
- Tastatur groß, Eingabe per Zahlenblock oder große Auswahlknöpfe. Auf dem Rechner geht auch die Tastatur.
- Auswahlknöpfe zeigen Bild und Wort, wenn jede Antwort ein Bild hat: Formen, Körper, ja und nein, links und rechts, Farben, Gesicht, Rücken und Füße (`OptionPicture`). Nicht beim Benennen einer Form (`shape_name`), dort wäre das Bild die Lösung. Die Löschtaste ist ein Radiergummi (siehe `docs/design-fuer-kinder.md`).
- Jedes Zeichen der Kinder hat sein eigenes Farbfeld, damit Geschwister sich auch an der Farbe unterscheiden.

## Ablauf für das Kind

Das Kind ist 6 und liest noch nicht. Was es verstehen muss, kommt als Stimme, Bild oder Symbol. Text ist für die Eltern. Olli spricht in der ersten Person und nie den Namen des Kindes aus, denn die Sprachausgabe des Browsers kann über einen Server laufen.

1. Start: Jedes Kind hat ein Zeichen wie an der Kita-Garderobe, die Eltern wählen es beim Anlegen. Das Tippen darauf schaltet Ton und Sprache frei.
2. Begrüßung: Olli sagt, was kommt. Das Kind tippt auf ▶.
3. Aufgabe: Olli liest sie vor, bei Antworten aus Wörtern auch jede Antwort. Die Antwort, die Olli gerade liest, leuchtet hellblau. Der Lautsprecher wiederholt alles.
   Antworten geht immer gleich: Zahl tippen oder Antwort antippen, ändern geht, erst der gelbe Haken prüft. Eine angetippte Antwort bekommt einen blauen Rand, Olli sagt das Wort, und steht in der Rechnung eine Lücke, rückt sie hinein. Nur "Weiß ich noch nicht" zählt sofort. Im Kopf nur das Haus und die zehn Plättchen.
4. Richtig: Zweiklang, Olli hüpft, Formen fliegen aus der Tafel, nach 1,1 s geht es weiter.
5. Falsch: Bei freier Eingabe sagt Olli "Schau nochmal." und das Kind hat einen zweiten Versuch. Danach zeigt Olli die Lösung, weiter mit →. Bei Auswahl gleich die Lösung, ein zweiter Versuch wäre dort geraten.
6. Standortcheck: Er probiert absichtlich zu Schweres, deshalb kein richtig oder falsch. Olli sagt "Gemerkt!". Das Fragezeichen ("Weiß ich noch nicht") senkt das Raten, Olli sagt "Das üben wir später." Ist der Check vorbei, sagt Olli: "Jetzt weiß ich, was du kannst."
7. Zurück zu den Grundlagen: Vor der nächsten Aufgabe sagt Olli "Wir üben erst etwas, das dir dabei hilft." Das klingt nach Werkzeug, nicht nach Abstieg.
8. Ende: Nach 10 Aufgaben gibt Olli einen Stempel mit Wellenrand. Blau mit Gesicht, rot mit Stern, wenn eine Kompetenz neu sitzt, darunter "Neu: …".

Das Zwanzigerfeld legt zeilenweise, obere Reihe zuerst: 8 + 5 zeigt die volle Zehn und 3 darunter. Gerade und ungerade legt es paarweise in Spalten, ein Plättchen ohne Partner heißt ungerade. Verdoppeln und Halbieren legt es gespiegelt, oben so viele wie unten.

Darstellungen: Das Backend nennt pro Aufgabe die erlaubten Darstellungen, `Figure` zeichnet die erste, die das Frontend kann. Sind es mehrere (etwa `bar_chart` und `table`), entscheidet die Aufgaben-ID, damit dieselbe Aufgabe ihr Bild behält. `plain` ist kein Bild. Gebaut sind `twenty_field`, `dice`, `scattered`, `number_line`, `shapes`, `grid`, `clock`, `digital_clock`, `money`, `lengths`, `units`, `ruler`, `bar_chart` und `table`. Nicht gezeichnet: `fingers` (die Würfelbilder springen ein) und `tally` (Zählaufgaben fallen auf das Zwanzigerfeld zurück). Alle Bilder sind Inline-SVG oder HTML und nehmen ihre Farben aus den Tokens, Gitter und Längen rechnen in Kästchen von 28 px. Die Operanden, die jedes Bild liest, stehen in `content/math/generators/README.md`.

Adressen: `/` Kind wählen, `/practice/<id>` üben, `/parent` Elternbereich. Neuladen bleibt auf der Seite, Zurück im Browser geht zur vorigen. Die Adresse trägt die ID des Kindes, nie den Namen. Unbekannte Adresse oder fremdes Kind: zurück zum Start. Anmelden und Onboarding haben keine eigene Adresse, sie liegen vor jeder Seite. Nach dem Abmelden geht es zum Start. Neuladen beim Üben beginnt die Sitzung neu mit der Begrüßung, im Elternbereich fragt die App wieder nach der PIN. Der Webserver muss für jeden Pfad `index.html` liefern (Vite tut das).

Onboarding: Nach dem Login fragt `App` das Backend nach Kindern und PIN. Fehlt etwas, kommt das Onboarding und zeigt nur die fehlenden Schritte: Kind mit Zeichen anlegen, PIN wählen (zweimal), Fertig. Danach übt das neue Kind sofort. Die PIN prüft das Backend. "PIN vergessen?" löscht die PIN und meldet ab. Nach dem Login mit Passwort fragt das Onboarding nach einer neuen PIN.
