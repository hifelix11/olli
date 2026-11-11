const BAR = 44;
const GAP = 24;
const X0 = 44;
const TOP = 12;
const BASE = 172;

type Props = { title: string; categories: string; values: string };

/** Säulendiagramm. Die Höhe steht nur an der Achse, nicht an der Säule. */
export function BarChart({ title, categories, values }: Props) {
  const cats = categories.split(" ").filter(Boolean);
  const vals = values.split(" ").filter(Boolean).map(Number);
  const max = Math.max(1, ...vals);
  const unit = (BASE - TOP) / max;
  const step = max > 10 ? 2 : 1;
  const w = X0 + cats.length * (BAR + GAP) + 8;
  return (
    <figure className="picture bar-chart">
      <figcaption>{title}</figcaption>
      <svg viewBox={`0 0 ${w} 200`} width={w} height="200" role="img" aria-label={`Säulendiagramm: ${title}`}>
        {Array.from({ length: Math.floor(max / step) + 1 }, (_, i) => {
          const y = BASE - i * step * unit;
          return (
            <g key={i}>
              <line x1={X0} y1={y} x2={w - 4} y2={y} stroke="var(--line)" strokeWidth="1" />
              <line x1={X0 - 6} y1={y} x2={X0} y2={y} stroke="var(--ink)" strokeWidth="2" />
              <text x={X0 - 10} y={y} textAnchor="end" dominantBaseline="central" fontSize="14" fill="var(--ink)">
                {i * step}
              </text>
            </g>
          );
        })}
        <line x1={X0} y1={TOP} x2={X0} y2={BASE} stroke="var(--ink)" strokeWidth="2" />
        {cats.map((cat, i) => {
          const x = X0 + GAP / 2 + i * (BAR + GAP);
          const v = vals[i] ?? 0;
          return (
            <g key={cat}>
              <rect x={x} y={BASE - v * unit} width={BAR} height={v * unit} fill="var(--blue)" />
              <text x={x + BAR / 2} y={BASE + 20} textAnchor="middle" fontSize="15" fill="var(--ink)">
                {cat}
              </text>
            </g>
          );
        })}
        <line x1={X0} y1={BASE} x2={w - 4} y2={BASE} stroke="var(--ink)" strokeWidth="2" />
      </svg>
    </figure>
  );
}
