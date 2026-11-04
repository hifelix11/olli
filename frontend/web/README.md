# frontend/web

Web-App als PWA: Kinderbereich (Aufgaben, Figur), Elternbereich (PIN, Lernstand als Karte). Nur Anzeige und Antwort. Alle Logik liegt im Backend.

Noch nicht angelegt. Anlegen mit:

```bash
cd frontend
npm create vite@latest web -- --template react-ts
cd web
npm install
npm run dev
```

Geplante Struktur:

```
src/
  api/              Client für das Backend
  representations/  plain, twenty_field, später Spielwelt
  child/            Kinderbereich
  parent/           Elternbereich
```
