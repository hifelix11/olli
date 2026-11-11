import type { ReactNode } from "react";
import { Shape } from "./Shapes";

/** Formen, die `Shape` zeichnen kann. "two_circles" zeigt zwei Kreise. */
const SHAPES = new Set([
  "circle",
  "semicircle",
  "triangle",
  "square",
  "rectangle",
  "quadrilateral",
  "pentagon",
  "hexagon",
]);

const SKIN = "#f6c49b";

const line = (d: string) => (
  <path
    d={d}
    fill="none"
    stroke="var(--ink)"
    strokeWidth="8"
    strokeLinecap="round"
    strokeLinejoin="round"
  />
);

/** Körper schräg von oben: die helle Fläche oben, die dunkle rechts. */
const SOLIDS: Record<string, ReactNode> = {
  cube: (
    <>
      <polygon className="tone-light" points="40,10 66,25 40,40 14,25" />
      <polygon fill="var(--blue)" points="14,25 40,40 40,70 14,55" />
      <polygon className="tone-dark" points="40,40 66,25 66,55 40,70" />
    </>
  ),
  cuboid: (
    <>
      <polygon className="tone-light" points="30,45 68,23 50,12 12,34" />
      <polygon fill="var(--blue)" points="12,34 30,45 30,69 12,58" />
      <polygon className="tone-dark" points="30,45 68,23 68,47 30,69" />
    </>
  ),
  sphere: (
    <>
      <circle cx="40" cy="40" r="30" fill="var(--blue)" />
      <circle cx="30" cy="29" r="8" className="tone-light" />
    </>
  ),
  cylinder: (
    <>
      <path d="M20 18 V62 A20 7 0 0 0 60 62 V18 Z" fill="var(--blue)" />
      <path d="M40 18 V69 A20 7 0 0 0 60 62 V18 Z" className="tone-dark" />
      <ellipse cx="40" cy="18" rx="20" ry="7" className="tone-light" />
    </>
  ),
  cone: (
    <>
      <path d="M40 10 L18 62 A22 7 0 0 0 40 69 Z" fill="var(--blue)" />
      <path d="M40 10 L62 62 A22 7 0 0 1 40 69 Z" className="tone-dark" />
    </>
  ),
  pyramid: (
    <>
      <polygon fill="var(--blue)" points="40,14 8,52 40,66" />
      <polygon className="tone-dark" points="40,14 40,66 72,52" />
    </>
  ),
};

/** Kopf und Schultern. Von vorn mit Gesicht, von hinten nur Haare. */
const shoulders = (
  <>
    <path d="M12 80 C12 62 24 57 40 57 C56 57 68 62 68 80 Z" fill="var(--blue)" />
    <rect x="34" y="44" width="12" height="16" fill={SKIN} />
  </>
);

const PEOPLE: Record<string, ReactNode> = {
  face: (
    <>
      {shoulders}
      <circle cx="40" cy="30" r="20" fill="var(--ink)" />
      <ellipse cx="40" cy="36" rx="16" ry="15" fill={SKIN} />
      <circle cx="33" cy="35" r="2.6" fill="var(--ink)" />
      <circle cx="47" cy="35" r="2.6" fill="var(--ink)" />
      <path d="M34 42 Q40 47 46 42" fill="none" stroke="var(--ink)" strokeWidth="2.6" strokeLinecap="round" />
    </>
  ),
  back: (
    <>
      {shoulders}
      <circle cx="20" cy="35" r="5" fill={SKIN} />
      <circle cx="60" cy="35" r="5" fill={SKIN} />
      <circle cx="40" cy="30" r="20" fill="var(--ink)" />
    </>
  ),
  feet: (
    <>
      <rect x="18" y="6" width="14" height="50" fill="var(--ink-soft)" />
      <rect x="48" y="6" width="14" height="50" fill="var(--ink-soft)" />
      <path d="M8 72 C8 58 16 52 25 52 C34 52 38 58 38 72 Z" fill="var(--blue)" />
      <path d="M42 72 C42 58 46 52 55 52 C64 52 72 58 72 72 Z" fill="var(--blue)" />
      <rect x="6" y="70" width="34" height="6" rx="3" fill="var(--ink)" />
      <rect x="40" y="70" width="34" height="6" rx="3" fill="var(--ink)" />
    </>
  ),
};

const SIGNS: Record<string, ReactNode> = {
  yes: line("M16 42 L32 58 L64 24"),
  correct: line("M16 42 L32 58 L64 24"),
  no: line("M22 22 L58 58 M58 22 L22 58"),
  incorrect: line("M22 22 L58 58 M58 22 L22 58"),
  left: line("M64 40 H16 M34 22 L16 40 L34 58"),
  right: line("M16 40 H64 M46 22 L64 40 L46 58"),
};

const COLORS: Record<string, string> = { red: "var(--red)", blue: "var(--blue)", green: "var(--green)" };

const picture = (drawing: ReactNode, key?: number) => (
  <svg key={key} viewBox="0 0 80 80" aria-hidden="true">
    {drawing}
  </svg>
);

/**
 * Bild zu einer Antwort, gefunden über ihren Wert ("circle", "two_triangles", "sphere", "yes").
 * null, wenn es keins gibt. Ein Erstklässler liest noch nicht: Bild und Wort zusammen.
 */
export function optionPicture(value: number | string): ReactNode | null {
  if (typeof value !== "string") return null;
  const two = /^two_(\w+)s$/.exec(value);
  const shape = two ? two[1] : value;
  if (SHAPES.has(shape)) {
    const drawing = <Shape id={shape} />;
    return two ? [picture(drawing, 0), picture(drawing, 1)] : picture(drawing);
  }
  const color = COLORS[value];
  const drawing =
    SOLIDS[value] ??
    PEOPLE[value] ??
    SIGNS[value] ??
    (color ? <circle cx="40" cy="40" r="30" fill={color} /> : null);
  return drawing ? picture(drawing) : null;
}
