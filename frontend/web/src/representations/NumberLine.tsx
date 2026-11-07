const STEP = 28;
const X0 = 20;
const Y = 46;

/** Zahlenstrahl von 0 bis 20, ein roter Pfeil zeigt auf n. Die Zahl an n steht nicht dran. */
export function NumberLine({ n }: { n: number }) {
  const x = X0 + n * STEP;
  return (
    <svg
      className="picture number-line"
      viewBox="0 0 600 84"
      role="img"
      aria-label="Zahlenstrahl von 0 bis 20 mit einem Pfeil"
    >
      <line x1={X0} y1={Y} x2={X0 + 20 * STEP} y2={Y} stroke="var(--ink)" strokeWidth="3" />
      {Array.from({ length: 21 }, (_, i) => {
        const tx = X0 + i * STEP;
        const big = i % 5 === 0;
        const len = big ? 11 : 6;
        return (
          <g key={i}>
            <line x1={tx} y1={Y - len} x2={tx} y2={Y + len} stroke="var(--ink)" strokeWidth={big ? 3 : 2} />
            {big && (
              <text x={tx} y={Y + 34} textAnchor="middle" fontSize="22" fontWeight="700" fill="var(--ink)">
                {i}
              </text>
            )}
          </g>
        );
      })}
      <polygon points={`${x},${Y - 13} ${x - 10},${Y - 32} ${x + 10},${Y - 32}`} fill="var(--red)" />
    </svg>
  );
}
