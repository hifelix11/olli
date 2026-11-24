# frontend/app

Die App in Flutter: Kinderbereich (Aufgaben, Olli, Zwanzigerfeld), Elternbereich (PIN, Lernstand als Karte). Eine Codebasis für Web, iPad und später Android. Nur Anzeige und Antwort. Alle Logik liegt im Backend.

Flutter zeichnet jede Fläche selbst. Das passt zu Olli: Die Oberfläche besteht aus eigenen Formen, nicht aus Bedienelementen des Systems.

```bash
flutter pub get                               # Pakete holen
flutter run -d web-server --web-port 5173     # dann http://localhost:5173 im Browser öffnen
flutter run -d chrome --web-port 5173         # öffnet Chrome selbst, falls installiert
flutter test
flutter analyze
dart format lib test                          # 100 Spalten, siehe analysis_options.yaml
flutter build web                             # Ergebnis in build/web
```

Das Backend muss auf Port 8000 laufen. Eine andere Adresse geht mit `--dart-define=API_URL=http://<adresse>:8000`. Der Port 5173 ist im Backend (CORS) und in Supabase eingetragen.

Pakete: `go_router` (Adressen), `http` (Aufrufe ans Backend), `flutter_secure_storage` (Tokens im Schlüsselbund), `path_parsing` (SVG-Pfaddaten für Olli, Zeichen und Symbole). Die Schrift Jost liegt als Datei in `fonts/`, nichts wird zur Laufzeit von fremden Servern geladen.

Anmeldung: Die App schickt E-Mail und Passwort ans Backend, nie an Supabase. `api/client.dart` hängt das Token an jede Anfrage. Bei 401 holt es einmal neue Tokens und wiederholt die Anfrage. Klappt das nicht, endet die Anmeldung und der Login erscheint. Die Kinderliste kommt vom Backend. Abmelden geht im Elternbereich, hinter der PIN.

## Struktur

Ordner nach Bereichen, keine Schichten. Die Fachlogik lebt im Backend.

```
lib/
  main.dart            Start, Adressen, Tor vor jeder Seite (Login, Onboarding)
  app_state.dart       Was die App teilt: Anmeldung, Kinder, was dem Konto fehlt
  api/                 client.dart (Aufrufe, Tokens), models.dart (Typen der API)
  ui/                  tokens.dart (Farben, Schrift), controls.dart (Knöpfe, Felder, Seitenrahmen),
                       icons.dart (Symbole statt Wörter), sketch.dart (Zeichnen wie in einem SVG)
  olli/olli_view.dart  Olli mit drei Stimmungen, hüpft bei fröhlich
  child/               practice_controller.dart (Ablauf der Sitzung, ohne Oberfläche),
                       practice_page.dart (Begrüßung, Üben, Ende), task_view.dart (Tafel und Antworten),
                       keypad.dart, stamp.dart, burst.dart (Formen bei richtig), sign.dart (Zeichen der Kinder)
  parent/              parent_area.dart (PIN, Kinder anlegen, Jahresziel und Karte), pin_pad.dart, sign_picker.dart
  start/               entry.dart (Rahmen: Olli auf Rosa, daneben das Formular), login_page.dart,
                       onboarding_page.dart, start_page.dart (Kind wählen)
  representations/     figure.dart wählt das Bild zur Aufgabe, counters.dart (Aufgabe → Plättchen),
                       sonst ein Bild pro Datei
test/                  Ablauf der Sitzung, Aufgaben-Helfer, die App gegen ein Backend-Double
```

Drei Stellen sind zum Austauschen gebaut, sonst gibt es keine Abstraktion:

- **`Api`**: das Backend. Tests geben ihm einen `MockClient`.
- **`OlliView`**: bekommt eine Stimmung und zeichnet Olli. Heute ein `CustomPainter`, später eine Rive-Datei.
- **Stimme**: fehlt noch, siehe unten. Ollis Sätze laufen an einer Stelle zusammen: `PracticeController.line`.

Der Ablauf ist von der Anzeige getrennt: `PracticeController` kennt die Phasen der Sitzung (`Loading`, `Welcome`, `Asking`, `Answered`, `Done`, `Failed`) und lässt sich ohne Oberfläche testen.

## Design

Die Formenkiste. Ollis Welt besteht aus flachen Formen, wie sie ein Kind in der ersten Jahrgangsstufe in der Hand hat: Wendeplättchen, Würfel, Dreiecke. Olli ist ein Otter als runder Kiesel mit Gesicht. Einfach wie ein Spiel, aber ohne Spielkonsole: keine 3D-Knöpfe, kein Lernpfad, kein Grün als Hauptfarbe.

| Token | Wert | Rolle |
| --- | --- | --- |
| Kreide (`chalk`) | `#F3F1F9` | Hintergrund |
| Tafel (`board`) | `#FFFFFF` | Aufgabe, Tasten, Felder |
| Nacht (`ink`) | `#24204A` | Text, Knöpfe für Eltern |
| Rot, Blau | `#F24C3D`, `#2E5BF0` | Wendeplättchen, Fortschritt |
| Sonne (`sun`) | `#FFC83D` | alles, was das Kind antippt, um weiterzukommen; Ende der Sitzung |
| Rosa (`pink`) | `#FFB8D9` | Start, Anmelden, Ollis Sprechblase |
| Olli | `#F08A3C`, `#FFE6CC` | Fell, Schnauze |
| Grün (`green`) | `#2FA562` | nur die Elternkarte: sitzt |

Alle Werte stehen in `lib/ui/tokens.dart`.

Schrift: Jost, 400 bis 800. Geometrisch wie die Druckschrift der Grundschule: einstöckiges a und g, einfache Striche. Zahlen in der Aufgabe 76 px (Telefon 54 px), Frage 28 px, Tastatur 34 px.

Regeln:

- Flach: keine Schatten, keine Verläufe. Formen sind rund, Knöpfe sind Pillen oder Kreise.
- Volle Farbe nur an den Rändern der Sitzung: Start rosa, Begrüßung blau, Ende gelb. Die Aufgabe selbst bleibt ruhig: weiße Tafel auf Kreide.
- Gelb heißt los: Play, Haken, Pfeil. Die Knöpfe für Eltern sind Nacht.
- Jeder Knopf gibt beim Drücken nach (`Tap` in `controls.dart`), Tasten werden dabei blau. Kinder erwarten auf jeden Tipp eine Antwort.
- Bewegung nur als Antwort: Olli hüpft bei richtig, Formen fliegen aus der Tafel, die Tafel wackelt beim zweiten Versuch, ein Plättchen ploppt in den Fortschritt, der Stempel fällt. Bittet das Gerät um weniger Bewegung, springt nichts.
- Olli sitzt auf der Kante der Tafel, die Sprechblase daneben. Olli und Tafel stehen als Gruppe in der Mitte. Antworten liegen unter der Tafel, auch der Zahlenblock: Die Ziffern 1 bis 0 stehen in einer Reihe, schmal in zwei Reihen, Löschen und Haken darunter. So bleibt er flach.
- Kein Scrollen beim Üben, solange der Platz reicht. Reicht er nicht, scrollt nur der Teil unter dem Kopf.
- Kein Text, den ein Erstklässler nicht braucht.
- Eine Sitzung hat 10 Aufgaben, sichtbar als zehn Plättchen oben, mit Lücke nach fünf. Danach ist Schluss, ohne "Noch eine Runde".
- Tastatur groß, Eingabe per Zahlenblock oder große Auswahlknöpfe. Auf dem Rechner geht auch die Tastatur: Ziffern, Löschen, Enter.
- Auswahlknöpfe zeigen Bild und Wort, wenn jede Antwort ein Bild hat: Formen, Körper, ja und nein, links und rechts, Farben, Gesicht, Rücken und Füße (`option_picture.dart`). Nicht beim Benennen einer Form (`shape_name`), dort wäre das Bild die Lösung. Die Löschtaste ist ein Radiergummi (siehe `docs/design-fuer-kinder.md`).
- Jedes Zeichen der Kinder hat sein eigenes Farbfeld, damit Geschwister sich auch an der Farbe unterscheiden.
- Bilder sind Code, keine Dateien: `Sketch` zeichnet in ein festes Koordinatenfeld und nimmt die Farben aus den Tokens.

## Ablauf für das Kind

Das Kind ist 6 und liest noch nicht. Was es verstehen muss, soll als Stimme, Bild oder Symbol kommen. Text ist für die Eltern.

**Stand: Olli spricht vorerst nur als Text.** Die Stimme des Geräts klingt zu schlecht, sie kommt nicht in die App. Geplant ist eine eigene Stimme über eine Schnittstelle. Bis dahin steht Ollis Satz in der Sprechblase und die Frage auf der Tafel. Für einen Test mit Kindern, die nicht lesen, muss ein Erwachsener vorlesen. Olli sagt nie den Namen des Kindes.

1. Start: Jedes Kind hat ein Zeichen wie an der Kita-Garderobe, die Eltern wählen es beim Anlegen.
2. Begrüßung: Olli sagt, was kommt. Das Kind tippt auf ▶.
3. Aufgabe: Antworten geht immer gleich: Zahl tippen oder Antwort antippen, ändern geht, erst der gelbe Haken prüft. Eine angetippte Antwort bekommt einen blauen Rand, und steht in der Rechnung eine Lücke, rückt sie hinein. Nur "Weiß ich noch nicht" zählt sofort. Im Kopf nur das Haus und die zehn Plättchen.
4. Richtig: Olli hüpft, Formen fliegen aus der Tafel, nach 1,1 s geht es weiter.
5. Falsch: Bei freier Eingabe sagt Olli "Schau nochmal." und das Kind hat einen zweiten Versuch. Danach zeigt Olli die Lösung, weiter mit →. Bei Auswahl gleich die Lösung, ein zweiter Versuch wäre dort geraten.
6. Standortcheck: Er probiert absichtlich zu Schweres, deshalb kein richtig oder falsch. Olli sagt "Gemerkt!". Das Fragezeichen ("Weiß ich noch nicht") senkt das Raten, Olli sagt "Das üben wir später." Ist der Check vorbei, sagt Olli: "Jetzt weiß ich, was du kannst."
7. Zurück zu den Grundlagen: Vor der nächsten Aufgabe sagt Olli "Wir üben erst etwas, das dir dabei hilft." Das klingt nach Werkzeug, nicht nach Abstieg.
8. Ende: Nach 10 Aufgaben gibt Olli einen Stempel mit Wellenrand. Blau mit Gesicht, rot mit Stern, wenn eine Kompetenz neu sitzt, darunter "Neu: …".

Das Zwanzigerfeld legt zeilenweise, obere Reihe zuerst: 8 + 5 zeigt die volle Zehn und 3 darunter. Gerade und ungerade legt es paarweise in Spalten, ein Plättchen ohne Partner heißt ungerade. Verdoppeln und Halbieren legt es gespiegelt, oben so viele wie unten.

Darstellungen: Das Backend nennt pro Aufgabe die erlaubten Darstellungen, `figureFor` zeichnet die erste, die die App kann. Sind es mehrere (etwa `bar_chart` und `table`), entscheidet die Aufgaben-ID, damit dieselbe Aufgabe ihr Bild behält. `plain` ist kein Bild. Gebaut sind `twenty_field`, `dice`, `scattered`, `number_line`, `shapes`, `grid`, `clock`, `digital_clock`, `money`, `lengths`, `units`, `ruler`, `bar_chart` und `table`. Nicht gezeichnet: `fingers` (die Würfelbilder springen ein) und `tally` (Zählaufgaben fallen auf das Zwanzigerfeld zurück). Gitter und Längen rechnen in Kästchen von 28 px. Die Operanden, die jedes Bild liest, stehen in `content/math/generators/README.md`.

Adressen: `/` Kind wählen, `/practice/<id>` üben, `/parent` Elternbereich. Neuladen bleibt auf der Seite, Zurück im Browser geht zur vorigen. Die Adresse trägt die ID des Kindes, nie den Namen. Unbekannte Adresse oder fremdes Kind: zurück zum Start. Anmelden und Onboarding haben keine eigene Adresse, sie liegen vor jeder Seite (`_Gate` in `main.dart`). Nach dem Abmelden geht es zum Start. Neuladen beim Üben beginnt die Sitzung neu mit der Begrüßung, im Elternbereich fragt die App wieder nach der PIN. Im Web muss der Server für jeden Pfad `index.html` liefern (`flutter run` tut das).

Onboarding: Nach dem Login fragt die App das Backend nach Kindern und PIN. Fehlt etwas, kommt das Onboarding und zeigt nur die fehlenden Schritte: Kind mit Zeichen anlegen, PIN wählen (zweimal), Fertig. Danach übt das neue Kind sofort. Die PIN prüft das Backend. "PIN vergessen?" löscht die PIN und meldet ab. Nach dem Login mit Passwort fragt das Onboarding nach einer neuen PIN.

## Offen

- [ ] Stimme für Olli über eine eigene Schnittstelle. Danach: Frage und Antworten vorlesen, Lautsprecher zum Wiederholen, Ton bei richtig.
- [ ] iPad: braucht Xcode. Der Ordner `ios/` ist angelegt, aber noch nie gebaut. Für das Backend im WLAN braucht iOS eine Ausnahme für unverschlüsseltes HTTP (`NSAllowsLocalNetworking`).
- [ ] App-Kennung: `com.example.olli` ist ein Platzhalter. Vor dem ersten Build für den Store ersetzen.
- [ ] App-Symbol: `web/icons/` und `ios/` zeigen noch das Flutter-Logo.
- [ ] Android: `flutter create --platforms android .` legt den Ordner an, sobald das SDK installiert ist.
- [ ] Olli als Rive-Datei, sobald es eine gibt.
- [ ] Plättchen schieben, mit dem Finger zeichnen: die Arbeitsfläche aus dem Konzept.
