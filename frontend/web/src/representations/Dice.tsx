/** Augen auf einem 3×3-Raster, wie auf dem Spielwürfel. */
const PIPS: Record<number, [number, number][]> = {
  1: [[1, 1]],
  2: [[0, 0], [2, 2]],
  3: [[0, 0], [1, 1], [2, 2]],
  4: [[0, 0], [2, 0], [0, 2], [2, 2]],
  5: [[0, 0], [2, 0], [1, 1], [0, 2], [2, 2]],
  6: [[0, 0], [2, 0], [0, 1], [2, 1], [0, 2], [2, 2]],
};

export function Dice({ n }: { n: number }) {
  const pips = PIPS[n] ?? [];
  return (
    <svg
      className="picture dice"
      viewBox="0 0 120 120"
      width="120"
      height="120"
      role="img"
      aria-label="Würfelbild"
    >
      <rect x="4" y="4" width="112" height="112" rx="18" fill="var(--paper)" stroke="var(--ink)" strokeWidth="3" />
      {pips.map(([c, r]) => (
        <circle key={`${c}${r}`} cx={30 + c * 30} cy={30 + r * 30} r="9" fill="var(--ink)" />
      ))}
    </svg>
  );
}
