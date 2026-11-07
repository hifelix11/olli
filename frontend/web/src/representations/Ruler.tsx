const STEP = 24;
const X0 = 16;

/** Ein Stab ab 0, darunter ein Lineal mit Zentimetern bis 20. */
export function Ruler({ n }: { n: number }) {
  return (
    <svg className="picture ruler" viewBox="0 0 520 96" role="img" aria-label="Ein Stab über einem Lineal">
      <rect x={X0} y="6" width={n * STEP} height="22" fill="var(--blue)" />
      <rect x="6" y="38" width="508" height="52" fill="var(--paper)" stroke="var(--ink)" strokeWidth="2" />
      {Array.from({ length: 21 }, (_, i) => {
        const x = X0 + i * STEP;
        const big = i % 5 === 0;
        return (
          <g key={i}>
            <line x1={x} y1="38" x2={x} y2={38 + (big ? 18 : 11)} stroke="var(--ink)" strokeWidth={big ? 2.5 : 1.5} />
            <text x={x} y="80" textAnchor="middle" fontSize="16" fill="var(--ink)">
              {i}
            </text>
          </g>
        );
      })}
      <text x="508" y="80" textAnchor="end" fontSize="13" fill="var(--ink-soft)">
        cm
      </text>
    </svg>
  );
}
