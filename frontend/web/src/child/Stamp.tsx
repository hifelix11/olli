import { useId } from "react";

/**
 * Der Stempel am Ende jeder Sitzung, wie die Lehrkraft ihn ins Heft drückt.
 * Blau mit Gesicht für eine geschaffte Sitzung, rot mit Stern, wenn etwas Neues sitzt.
 */
export function Stamp({ special, size = 168 }: { special: boolean; size?: number }) {
  const path = useId();
  return (
    <svg
      className={`stamp ${special ? "stamp-special" : ""}`}
      width={size}
      height={size}
      viewBox="0 0 120 120"
      role="img"
      aria-label={special ? "Stempel mit Stern" : "Stempel"}
    >
      <defs>
        <path id={path} d="M60,60 m-46,0 a46,46 0 1,1 92,0 a46,46 0 1,1 -92,0" />
      </defs>
      <g fill="none" stroke="currentColor">
        <circle cx="60" cy="60" r="55" strokeWidth="4" />
        <circle cx="60" cy="60" r="38" strokeWidth="2" />
      </g>
      <text fill="currentColor" fontSize="11" fontWeight="700" letterSpacing="1">
        <textPath href={`#${path}`} textLength="286" lengthAdjust="spacing">
          GUT GEÜBT ★ OLLI ★ GUT GEÜBT ★ OLLI ★
        </textPath>
      </text>
      {special ? (
        <polygon
          points="60,34 66.2,51.2 84.5,51.9 70.2,63.2 75.2,80.8 60,70.6 44.8,80.8 49.8,63.2 35.5,51.9 53.8,51.2"
          fill="currentColor"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
        />
      ) : (
        <g stroke="currentColor" strokeWidth="4" strokeLinecap="round" fill="none">
          <circle cx="49" cy="52" r="1.5" fill="currentColor" />
          <circle cx="71" cy="52" r="1.5" fill="currentColor" />
          <path d="M46 66 q14 14 28 0" />
        </g>
      )}
    </svg>
  );
}
