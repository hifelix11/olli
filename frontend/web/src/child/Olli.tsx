export type Mood = "neutral" | "happy" | "thinking";

/** Olli, der Otter. Nur ein Gesicht mit drei Stimmungen. */
export function Olli({ mood = "neutral", size = 72 }: { mood?: Mood; size?: number }) {
  const fur = "#8b5e3c";
  const light = "#e8c9a8";
  const ink = "#1d2b50";
  return (
    <svg
      className={`olli olli-${mood}`}
      width={size}
      height={size}
      viewBox="0 0 100 100"
      role="img"
      aria-label="Olli"
    >
      <circle cx="20" cy="28" r="11" fill={fur} />
      <circle cx="80" cy="28" r="11" fill={fur} />
      <circle cx="20" cy="28" r="5" fill={light} />
      <circle cx="80" cy="28" r="5" fill={light} />
      <ellipse cx="50" cy="54" rx="40" ry="38" fill={fur} />
      <ellipse cx="50" cy="66" rx="24" ry="18" fill={light} />
      {mood === "happy" ? (
        <>
          <path d="M28 44 q7 -8 14 0" stroke={ink} strokeWidth="4" fill="none" strokeLinecap="round" />
          <path d="M58 44 q7 -8 14 0" stroke={ink} strokeWidth="4" fill="none" strokeLinecap="round" />
        </>
      ) : (
        <>
          <circle cx="35" cy="44" r="4.5" fill={ink} />
          <circle cx="65" cy="44" r="4.5" fill={ink} />
        </>
      )}
      <ellipse cx="50" cy="60" rx="7" ry="5" fill={ink} />
      {mood === "thinking" ? (
        <path d="M42 74 h12" stroke={ink} strokeWidth="3.5" strokeLinecap="round" />
      ) : (
        <path d="M40 70 q10 10 20 0" stroke={ink} strokeWidth="3.5" fill="none" strokeLinecap="round" />
      )}
      <path d="M26 62 h12 M26 68 h12 M62 62 h12 M62 68 h12" stroke={ink} strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
