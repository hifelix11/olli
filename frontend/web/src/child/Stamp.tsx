/** Rand aus zwölf Bögen, wie ein Aufkleber mit Wellenkante. */
const BUMPS = Array.from({ length: 12 }, (_, i) => {
  const a = (2 * Math.PI * i) / 12;
  return [60 + 44 * Math.cos(a), 60 + 44 * Math.sin(a)] as const;
});

/**
 * Der Stempel am Ende jeder Sitzung.
 * Blau mit Gesicht für eine geschaffte Sitzung, rot mit Stern, wenn etwas Neues sitzt.
 */
export function Stamp({ special, size = 184 }: { special: boolean; size?: number }) {
  return (
    <svg
      className={`stamp${special ? " stamp-special" : ""}`}
      width={size}
      height={size}
      viewBox="0 0 120 120"
      role="img"
      aria-label={special ? "Stempel mit Stern" : "Stempel"}
    >
      <g fill="currentColor">
        <circle cx="60" cy="60" r="46" />
        {BUMPS.map(([x, y], i) => (
          <circle key={i} cx={x.toFixed(1)} cy={y.toFixed(1)} r="13" />
        ))}
      </g>
      {special ? (
        <polygon
          points="60,30 67.6,49.6 88.5,50.7 72.3,63.9 77.6,84.3 60,72.9 42.4,84.3 47.7,63.9 31.5,50.7 52.4,49.6"
          fill="#fff"
          stroke="#fff"
          strokeWidth="4"
          strokeLinejoin="round"
        />
      ) : (
        <g fill="#fff">
          <circle cx="47" cy="52" r="6" />
          <circle cx="73" cy="52" r="6" />
          <path d="M42 66q18 22 36 0Z" stroke="#fff" strokeWidth="3" strokeLinejoin="round" />
        </g>
      )}
    </svg>
  );
}
