export type Mood = "neutral" | "happy" | "thinking";

const FUR = "#f08a3c";
const DARK = "#d9702a";
const CREAM = "#ffe6cc";
const INK = "#24204a";
const CHEEK = "#ff9ec4";

/** Olli, der Otter: ein runder Kiesel mit kleinen Ohren, heller Schnauze und Schnurrhaaren. */
export function Olli({ mood = "neutral", size = 72 }: { mood?: Mood; size?: number }) {
  const happy = mood === "happy";
  const look = mood === "thinking" ? { x: 1.5, y: -2 } : { x: 0, y: 0 };
  return (
    <svg
      className={`olli olli-${mood}`}
      width={size}
      height={size}
      viewBox="0 0 120 120"
      role="img"
      aria-label="Olli"
    >
      <circle cx="24" cy="40" r="9" fill={FUR} />
      <circle cx="96" cy="40" r="9" fill={FUR} />
      <circle cx="24" cy="40" r="4" fill={DARK} />
      <circle cx="96" cy="40" r="4" fill={DARK} />
      {happy ? (
        <>
          <rect x="3" y="50" width="16" height="30" rx="8" fill={DARK} transform="rotate(-30 11 65)" />
          <rect x="101" y="50" width="16" height="30" rx="8" fill={DARK} transform="rotate(30 109 65)" />
        </>
      ) : (
        <>
          <rect x="9" y="76" width="16" height="28" rx="8" fill={DARK} transform="rotate(16 17 90)" />
          <rect x="95" y="76" width="16" height="28" rx="8" fill={DARK} transform="rotate(-16 103 90)" />
        </>
      )}
      <path d="M60 22C90 22 106 40 107 68C108 98 90 116 60 116C30 116 12 98 13 68C14 40 30 22 60 22Z" fill={FUR} />
      <ellipse cx="60" cy="104" rx="24" ry="10" fill={CREAM} />
      <ellipse cx="60" cy="71" rx="27" ry="16" fill={CREAM} />
      <g stroke={INK} strokeWidth="2.2" strokeLinecap="round" opacity="0.7">
        <path d="M36 70l-14-3M36 75l-14 2M84 70l14-3M84 75l14 2" />
      </g>
      {happy && (
        <>
          <ellipse cx="34" cy="60" rx="6" ry="3.6" fill={CHEEK} />
          <ellipse cx="86" cy="60" rx="6" ry="3.6" fill={CHEEK} />
        </>
      )}
      {happy ? (
        <g stroke={INK} strokeWidth="4" strokeLinecap="round" fill="none">
          <path d="M40 55q6-8 12 0" />
          <path d="M68 55q6-8 12 0" />
        </g>
      ) : (
        <g>
          <circle cx={46 + look.x} cy={52 + look.y} r="5.5" fill={INK} />
          <circle cx={74 + look.x} cy={52 + look.y} r="5.5" fill={INK} />
          <circle cx={48 + look.x} cy={50 + look.y} r="1.8" fill="#fff" />
          <circle cx={76 + look.x} cy={50 + look.y} r="1.8" fill="#fff" />
        </g>
      )}
      {mood === "thinking" && <path d="M67 40l13-4" stroke={INK} strokeWidth="3.5" strokeLinecap="round" />}
      <ellipse cx="60" cy="64" rx="7.5" ry="5" fill={INK} />
      {happy ? (
        <path d="M51 71q9 13 18 0Z" fill={INK} stroke={INK} strokeWidth="2" strokeLinejoin="round" />
      ) : mood === "thinking" ? (
        <circle cx="61" cy="75" r="3" fill={INK} />
      ) : (
        <path
          d="M52 71q4 5 8 0q4 5 8 0"
          stroke={INK}
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
      )}
    </svg>
  );
}
