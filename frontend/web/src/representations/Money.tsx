function Coin({ value, unit }: { value: number; unit: string }) {
  return (
    <svg viewBox="0 0 64 64" width="64" height="64" aria-hidden="true">
      <circle cx="32" cy="32" r="29" fill="var(--paper)" stroke="var(--ink)" strokeWidth="3" />
      <circle cx="32" cy="32" r="23" fill="none" stroke="var(--ink)" strokeWidth="1" />
      <text x="32" y="32" textAnchor="middle" dominantBaseline="central" fontSize="16" fontWeight="700" fill="var(--ink)">
        {value} {unit}
      </text>
    </svg>
  );
}

function Note({ value }: { value: number }) {
  return (
    <svg viewBox="0 0 100 56" width="100" height="56" aria-hidden="true">
      <rect x="2" y="2" width="96" height="52" rx="4" fill="var(--paper)" stroke="var(--ink)" strokeWidth="3" />
      <rect x="10" y="10" width="80" height="36" fill="none" stroke="var(--ink)" strokeWidth="1" />
      <text x="50" y="28" textAnchor="middle" dominantBaseline="central" fontSize="20" fontWeight="700" fill="var(--ink)">
        {value} €
      </text>
    </svg>
  );
}

/** Münzen und Scheine in einer Reihe. Ab 5 € ist es ein Schein. */
export function Money({ coins, unit }: { coins: string; unit: string }) {
  const values = coins.split(" ").filter(Boolean).map(Number);
  return (
    <div className="picture money" role="img" aria-label="Münzen und Scheine">
      {values.map((value, i) =>
        unit === "€" && value >= 5 ? <Note key={i} value={value} /> : <Coin key={i} value={value} unit={unit} />,
      )}
    </div>
  );
}
