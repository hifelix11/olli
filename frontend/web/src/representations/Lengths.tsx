const CELL = 28; // ein Kästchen
const X0 = 36;
const MAX = 10;

function Bar({ label, value, y }: { label: string; value: number; y: number }) {
  return (
    <g>
      <text x="12" y={y + CELL / 2} textAnchor="middle" dominantBaseline="central" fontSize="22" fontWeight="700" fill="var(--ink)">
        {label}
      </text>
      <rect x={X0} y={y} width={value * CELL} height={CELL} fill="var(--blue)" />
    </g>
  );
}

/** Zwei Stäbe A und B, linksbündig, Länge in Kästchen. */
export function Lengths({ a, b }: { a: number; b: number }) {
  const w = X0 + MAX * CELL + 8;
  return (
    <svg className="picture lengths" viewBox={`0 0 ${w} 84`} width={w} height="84" role="img" aria-label="Zwei Stäbe A und B">
      <Bar label="A" value={a} y={6} />
      <Bar label="B" value={b} y={50} />
    </svg>
  );
}
