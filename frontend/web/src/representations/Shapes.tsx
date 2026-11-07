/** Ecken eines regelmäßigen Vielecks um (40, 40), erste Ecke oben. */
function regular(sides: number, r: number): string {
  return Array.from({ length: sides }, (_, i) => {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / sides;
    return `${(40 + r * Math.cos(a)).toFixed(1)},${(40 + r * Math.sin(a)).toFixed(1)}`;
  }).join(" ");
}

function Shape({ id, rotation }: { id: string; rotation: number }) {
  const fill = "var(--blue)";
  const transform = `rotate(${rotation} 40 40)`;
  switch (id) {
    case "circle":
      return <circle cx="40" cy="40" r="30" fill={fill} />;
    case "square":
      return <rect x="14" y="14" width="52" height="52" fill={fill} transform={transform} />;
    case "rectangle":
      return <rect x="6" y="22" width="68" height="36" fill={fill} transform={transform} />;
    case "triangle":
      return <polygon points="40,8 70,66 10,66" fill={fill} transform={transform} />;
    case "quadrilateral":
      return <polygon points="22,12 66,18 72,66 8,60" fill={fill} transform={transform} />;
    case "pentagon":
      return <polygon points={regular(5, 32)} fill={fill} transform={transform} />;
    case "hexagon":
      return <polygon points={regular(6, 32)} fill={fill} transform={transform} />;
    default:
      return null;
  }
}

/** Eine Reihe Formen, jede in ihrem Kästchen. `_` ist eine Lücke mit Fragezeichen. */
export function Shapes({ shapes, rotation }: { shapes: string; rotation: number }) {
  const ids = shapes.split(" ").filter(Boolean);
  return (
    <div
      className="picture shape-row"
      role="img"
      aria-label={ids.length === 1 ? "Eine Form" : "Eine Reihe aus Formen"}
    >
      {ids.map((id, i) =>
        id === "_" ? (
          <span key={i} className="shape-gap">
            ?
          </span>
        ) : (
          <svg key={i} className="shape" viewBox="0 0 80 80" aria-hidden="true">
            <Shape id={id} rotation={rotation} />
          </svg>
        ),
      )}
    </div>
  );
}
