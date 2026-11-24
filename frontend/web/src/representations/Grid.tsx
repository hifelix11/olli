const CELL = 28; // ein Kästchen

type Point = [number, number];

const parsePoints = (s: string): Point[] =>
  s
    .split(" ")
    .filter(Boolean)
    .map((p) => p.split(",").map(Number) as Point);

const parseMarks = (s: string): { label: string; at: Point }[] =>
  s
    .split(" ")
    .filter(Boolean)
    .map((m) => {
      const [label, at] = m.split(":");
      return { label, at: at.split(",").map(Number) as Point };
    });

type CellsProps = {
  width: number;
  height: number;
  filled: Point[];
  axis?: string;
  start?: Point;
  marks?: { label: string; at: Point }[];
};

/** Ein Gitter. x nach rechts, y nach unten, Zeile 0 oben. */
function Cells({ width, height, filled, axis, start, marks = [] }: CellsProps) {
  const w = width * CELL;
  const h = height * CELL;
  return (
    <svg viewBox={`-2 -2 ${w + 4} ${h + 4}`} width={w + 4} height={h + 4} aria-hidden="true">
      <rect x="0" y="0" width={w} height={h} fill="var(--board)" />
      {filled.map(([x, y]) => (
        <rect key={`${x},${y}`} x={x * CELL} y={y * CELL} width={CELL} height={CELL} fill="var(--blue)" />
      ))}
      {Array.from({ length: width + 1 }, (_, i) => (
        <line key={`v${i}`} x1={i * CELL} y1="0" x2={i * CELL} y2={h} stroke="var(--ink-soft)" strokeWidth="1" />
      ))}
      {Array.from({ length: height + 1 }, (_, i) => (
        <line key={`h${i}`} x1="0" y1={i * CELL} x2={w} y2={i * CELL} stroke="var(--ink-soft)" strokeWidth="1" />
      ))}
      <rect x="0" y="0" width={w} height={h} fill="none" stroke="var(--ink)" strokeWidth="2" />
      {axis === "vertical" && (
        <line
          x1={(width / 2) * CELL}
          y1="-2"
          x2={(width / 2) * CELL}
          y2={h + 2}
          stroke="var(--red)"
          strokeWidth="3"
          strokeDasharray="6 5"
        />
      )}
      {start && <circle cx={(start[0] + 0.5) * CELL} cy={(start[1] + 0.5) * CELL} r="9" fill="var(--red)" />}
      {marks.map(({ label, at }) => (
        <text
          key={label}
          x={(at[0] + 0.5) * CELL}
          y={(at[1] + 0.5) * CELL}
          textAnchor="middle"
          dominantBaseline="central"
          fontSize="18"
          fontWeight="700"
          fill="var(--ink)"
        >
          {label}
        </text>
      ))}
    </svg>
  );
}

type Props = {
  width: number;
  height: number;
  cells: string;
  copy: string;
  axis: string;
  start: string;
  marks: string;
};

/** Gitterfigur: gefüllte Kästchen, Spiegelachse, Startpunkt, Buchstaben. Mit `copy` daneben eine zweite Figur. */
export function Grid({ width, height, cells, copy, axis, start, marks }: Props) {
  const template = (
    <Cells
      width={width}
      height={height}
      filled={parsePoints(cells)}
      axis={axis}
      start={parsePoints(start)[0]}
      marks={parseMarks(marks)}
    />
  );
  if (!copy) {
    return (
      <div className="picture grid-figure" role="img" aria-label="Gitter">
        {template}
      </div>
    );
  }
  return (
    <div className="picture grid-pair" role="img" aria-label="Vorlage und Kopie im Gitter">
      <div>
        {template}
        <span>Vorlage</span>
      </div>
      <div>
        <Cells width={width} height={height} filled={parsePoints(copy)} />
        <span>Kopie</span>
      </div>
    </div>
  );
}
