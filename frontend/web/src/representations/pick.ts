import type { Task } from "../api/client";

/** Darstellungen, die das Frontend zeichnen kann. `plain` ist keine. */
const RENDERABLE = [
  "twenty_field",
  "dice",
  "scattered",
  "number_line",
  "shapes",
  "grid",
  "clock",
  "digital_clock",
  "money",
  "lengths",
  "units",
  "ruler",
  "bar_chart",
  "table",
];

/** Kleine Zahl aus der Aufgaben-ID, damit dieselbe Aufgabe immer dasselbe Bild bekommt. */
export function seedOf(id: string): number {
  let h = 7;
  for (let i = 0; i < id.length; i++) h = (Math.imul(h, 31) + id.charCodeAt(i)) >>> 0;
  return h;
}

/** Erste zeichenbare Darstellung der Aufgabe. Bei mehreren entscheidet die ID. Zählaufgaben zeigen immer ein Bild. */
export function pickRepresentation(task: Task): string | null {
  const renderable = task.representations.filter((r) => RENDERABLE.includes(r));
  if (renderable.length === 0) return task.kind === "count" ? "twenty_field" : null;
  return renderable[seedOf(task.id) % renderable.length];
}
