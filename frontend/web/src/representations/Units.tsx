const UNIT = 36;

/** Ein Stab, darunter n Büroklammern (oder eine andere Einheit) Stück an Stück. */
export function Units({ n, unit }: { n: number; unit: string }) {
  const w = n * UNIT + 16;
  return (
    <svg className="picture units" viewBox={`0 0 ${w} 76`} width={w} height="76" role="img" aria-label={`Ein Stab und ${unit} darunter`}>
      <rect x="8" y="8" width={n * UNIT} height="20" fill="var(--blue)" />
      {Array.from({ length: n }, (_, i) => {
        const cx = 8 + (i + 0.5) * UNIT;
        return (
          <g key={i}>
            <ellipse cx={cx} cy="52" rx="16" ry="8" fill="none" stroke="var(--ink)" strokeWidth="2.5" />
            <ellipse cx={cx} cy="52" rx="10" ry="4" fill="none" stroke="var(--ink)" strokeWidth="1.5" />
          </g>
        );
      })}
    </svg>
  );
}
