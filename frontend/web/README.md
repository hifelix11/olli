# frontend/web

Web-App als PWA: Kinderbereich (Aufgaben, Figur), Elternbereich (PIN, Lernstand als Karte). Nur Anzeige und Antwort. Alle Logik liegt im Backend.

Vite + React 19 + TypeScript, Linter: oxlint.

```bash
npm install
npm run dev       # http://localhost:5173
npm run build     # tsc + vite build
npm run lint
```

Geplante Struktur:

```
src/
  api/              Client für das Backend
  representations/  plain, twenty_field, später Spielwelt
  child/            Kinderbereich
  parent/           Elternbereich
```
