import type { CSSProperties } from "react";

const COLORS = ["var(--sun)", "var(--blue)", "var(--red)", "var(--pink)"];
const SHAPES = ["circle", "square", "triangle"];

/** Zwölf Formen im Kreis, abwechselnd nah und fern. */
const PIECES = Array.from({ length: 12 }, (_, i) => {
  const angle = (i / 12) * 2 * Math.PI + 0.2;
  const distance = i % 2 ? 250 : 340;
  return {
    shape: SHAPES[i % 3],
    style: {
      "--x": `${Math.round(Math.cos(angle) * distance)}px`,
      "--y": `${Math.round(Math.sin(angle) * distance * 0.6)}px`,
      "--r": `${i * 47}deg`,
      "--c": COLORS[i % 4],
    } as CSSProperties,
  };
});

/** Richtig! Ein Schwung Formen fliegt aus der Mitte der Tafel. */
export function Burst() {
  return (
    <div className="burst" aria-hidden="true">
      {PIECES.map((piece, i) => (
        <i key={i} className={piece.shape} style={piece.style} />
      ))}
    </div>
  );
}
