const COLS = 5;
const ROWS = 4;
const SLOT = 56;
const RADIUS = 16;
const JITTER = 10; // Nachbarplätze bleiben mindestens 36 auseinander, Plättchen sind 32 breit

/** Kleiner Zufallsgenerator mit Startwert, damit die Plättchen bei jedem Rendern gleich liegen. */
function lcg(seed: number): () => number {
  let s = seed >>> 0 || 1;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

/** n Plättchen ungeordnet in einem Kasten. */
export function Scattered({ n, seed }: { n: number; seed: number }) {
  const next = lcg(seed);
  const slots = Array.from({ length: COLS * ROWS }, (_, i) => i);
  for (let i = slots.length - 1; i > 0; i--) {
    const j = Math.floor(next() * (i + 1));
    [slots[i], slots[j]] = [slots[j], slots[i]];
  }
  const points = slots.slice(0, Math.min(n, slots.length)).map((slot) => ({
    x: (slot % COLS) * SLOT + SLOT / 2 + (next() * 2 - 1) * JITTER,
    y: Math.floor(slot / COLS) * SLOT + SLOT / 2 + (next() * 2 - 1) * JITTER,
  }));
  const w = COLS * SLOT;
  const h = ROWS * SLOT;
  return (
    <svg
      className="picture scattered"
      viewBox={`0 0 ${w} ${h}`}
      width={w}
      height={h}
      role="img"
      aria-label="Verstreute Plättchen"
    >
      {points.map((p, i) => (
        <circle key={i} cx={p.x.toFixed(1)} cy={p.y.toFixed(1)} r={RADIUS} fill="var(--blue)" />
      ))}
    </svg>
  );
}
