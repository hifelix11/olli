import type { ReactNode } from "react";
import type { Sign } from "../api/client";
import { SIGN_NAMES } from "./signs";

const INK = "#24204a";
const SUN = "#ffc83d";
const RED = "#f24c3d";
const BLUE = "#2e5bf0";
const ORANGE = "#f08a3c";
const GREEN = "#2fa562";
const VIOLET = "#7c5cf0";

/** Kleines Gesicht wie bei Olli: zwei Punkte, ein Lächeln. */
const face = (cx: number, cy: number, color = INK) => (
  <g fill={color}>
    <circle cx={cx - 2} cy={cy - 0.6} r="0.85" />
    <circle cx={cx + 2} cy={cy - 0.6} r="0.85" />
    <path d={`M${cx - 1.3} ${cy + 1}q1.3 1.4 2.6 0`} stroke={color} strokeWidth="0.8" strokeLinecap="round" fill="none" />
  </g>
);

const ring = (n: number, r: number, cx = 12, cy = 12) =>
  Array.from({ length: n }, (_, i) => {
    const a = (2 * Math.PI * i) / n - Math.PI / 2;
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)] as const;
  });

/** Jedes Zeichen hat sein Feld, damit Geschwister sich auch an der Farbe unterscheiden. */
const SIGNS: Record<Sign, { tile: string; drawing: ReactNode }> = {
  sun: {
    tile: "#dce5ff",
    drawing: (
      <>
        {ring(8, 1).map(([x, y], i) => (
          <line
            key={i}
            x1={12 + (x - 12) * 6.8}
            y1={12 + (y - 12) * 6.8}
            x2={12 + (x - 12) * 9.2}
            y2={12 + (y - 12) * 9.2}
            stroke={SUN}
            strokeWidth="1.9"
            strokeLinecap="round"
          />
        ))}
        <circle cx="12" cy="12" r="5.2" fill={SUN} />
        {face(12, 12)}
      </>
    ),
  },
  moon: {
    tile: "#2e2a66",
    drawing: (
      <>
        <path d="M14.5 4.5A7.8 7.8 0 1 0 19.8 15A6.2 6.2 0 1 1 14.5 4.5Z" fill={SUN} />
        <circle cx="10.2" cy="12.4" r="0.85" fill={INK} />
        <path d="M9.2 14.4q1.1 1.1 2.2 0" stroke={INK} strokeWidth="0.8" strokeLinecap="round" fill="none" />
      </>
    ),
  },
  star: {
    tile: "#eae3ff",
    drawing: (
      <>
        <polygon
          points="12,3.6 14.4,9.2 20.4,9.6 15.8,13.5 17.3,19.4 12,16.2 6.7,19.4 8.2,13.5 3.6,9.6 9.6,9.2"
          fill={SUN}
          stroke={SUN}
          strokeWidth="1.6"
          strokeLinejoin="round"
        />
        {face(12, 12.4)}
      </>
    ),
  },
  heart: {
    tile: "#ffddd8",
    drawing: (
      <>
        <path d="M12 20s-7.5-4.6-8.6-9.6A4.6 4.6 0 0 1 12 7a4.6 4.6 0 0 1 8.6 3.4C19.5 15.4 12 20 12 20z" fill={RED} />
        {face(12, 12.2, "#fff")}
      </>
    ),
  },
  fish: {
    tile: "#d4f1ec",
    drawing: (
      <>
        <path d="M15 12L21 7.4V16.6Z" fill={ORANGE} strokeLinejoin="round" />
        <ellipse cx="10" cy="12" rx="7" ry="5" fill={ORANGE} />
        <circle cx="6.8" cy="11" r="1.3" fill="#fff" />
        <circle cx="6.8" cy="11" r="0.7" fill={INK} />
      </>
    ),
  },
  apple: {
    tile: "#e0f3d9",
    drawing: (
      <>
        <path
          d="M12 8.6c-2-1.4-7.6-1.4-7.6 4.6 0 4 3 7.6 5 7.6 1 0 1.6-.5 2.6-.5s1.6.5 2.6.5c2 0 5-3.6 5-7.6 0-6-5.6-6-7.6-4.6z"
          fill={RED}
        />
        <path d="M12 8.6V5" stroke={INK} strokeWidth="1.4" strokeLinecap="round" />
        <path d="M12.6 5.6c1-2 3.2-2.6 4.8-2-.6 1.6-2.8 2.6-4.8 2z" fill={GREEN} />
      </>
    ),
  },
  flower: {
    tile: "#ffefc4",
    drawing: (
      <>
        {ring(5, 4.8).map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r="3.6" fill={VIOLET} />
        ))}
        <circle cx="12" cy="12" r="3" fill={ORANGE} />
      </>
    ),
  },
  boat: {
    tile: "#ffe3cc",
    drawing: (
      <>
        <path d="M11.6 3.6V15" stroke={INK} strokeWidth="1.4" strokeLinecap="round" />
        <path d="M12.8 4.4L19 13.6H12.8Z" fill={RED} strokeLinejoin="round" />
        <path d="M3 15.4H21L17.6 20.4H6.4Z" fill={BLUE} strokeLinejoin="round" />
      </>
    ),
  },
};

/** Das Zeichen eines Kindes auf seinem Farbfeld. */
export function SignIcon({ sign, size = 48 }: { sign: Sign; size?: number }) {
  const { tile, drawing } = SIGNS[sign];
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" role="img" aria-label={SIGN_NAMES[sign]}>
      <rect width="24" height="24" rx="7" fill={tile} />
      {drawing}
    </svg>
  );
}
