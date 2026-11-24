const C = 100;

/** Punkt auf dem Zifferblatt: Winkel ab 12 Uhr im Uhrzeigersinn, Abstand r von der Mitte. */
const point = (angle: number, r: number) => ({ x: C + r * Math.sin(angle), y: C - r * Math.cos(angle) });

const f = (v: number) => v.toFixed(1);

/** Analoguhr. Der Stundenzeiger wandert mit den Minuten weiter, bei halb steht er in der Mitte. */
export function Clock({ hour, minute }: { hour: number; minute: number }) {
  const hourHand = point((((hour % 12) + minute / 60) / 12) * 2 * Math.PI, 48);
  const minuteHand = point((minute / 60) * 2 * Math.PI, 70);
  return (
    <svg className="picture clock" viewBox="0 0 200 200" width="200" height="200" role="img" aria-label="Uhr">
      <circle cx={C} cy={C} r="92" fill="var(--board)" stroke="var(--ink)" strokeWidth="3" />
      {Array.from({ length: 12 }, (_, i) => {
        const a = ((i + 1) / 12) * 2 * Math.PI;
        const label = point(a, 74);
        const tickIn = point(a, 85);
        const tickOut = point(a, 92);
        return (
          <g key={i}>
            <line x1={f(tickIn.x)} y1={f(tickIn.y)} x2={f(tickOut.x)} y2={f(tickOut.y)} stroke="var(--ink)" strokeWidth="3" />
            <text
              x={f(label.x)}
              y={f(label.y)}
              textAnchor="middle"
              dominantBaseline="central"
              fontSize="18"
              fontWeight="700"
              fill="var(--ink)"
            >
              {i + 1}
            </text>
          </g>
        );
      })}
      <line x1={C} y1={C} x2={f(hourHand.x)} y2={f(hourHand.y)} stroke="var(--ink)" strokeWidth="7" strokeLinecap="round" />
      <line x1={C} y1={C} x2={f(minuteHand.x)} y2={f(minuteHand.y)} stroke="var(--ink)" strokeWidth="4" strokeLinecap="round" />
      <circle cx={C} cy={C} r="5" fill="var(--ink)" />
    </svg>
  );
}
