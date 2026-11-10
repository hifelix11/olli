import type { ReactNode } from "react";
import type { Sign } from "../api/client";
import { SIGN_NAMES } from "./signs";

const RED = "#e0442f";
const BLUE = "#2e62d9";
const INK = "#1d2b50";
const PAPER = "#fcfbf7";

const ring = (n: number, r: number, cx = 12, cy = 12) =>
  Array.from({ length: n }, (_, i) => {
    const a = (2 * Math.PI * i) / n - Math.PI / 2;
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)] as const;
  });

const DRAWINGS: Record<Sign, ReactNode> = {
  sun: (
    <>
      <circle cx="12" cy="12" r="4.5" fill={RED} />
      {ring(8, 1).map(([x, y], i) => (
        <line
          key={i}
          x1={12 + (x - 12) * 6.5}
          y1={12 + (y - 12) * 6.5}
          x2={12 + (x - 12) * 9.5}
          y2={12 + (y - 12) * 9.5}
          stroke={RED}
          strokeWidth="1.8"
          strokeLinecap="round"
        />
      ))}
    </>
  ),
  moon: <path d="M15 3.5A8.5 8.5 0 1 0 20.5 15A6.5 6.5 0 1 1 15 3.5Z" fill={BLUE} />,
  star: (
    <polygon
      points="12,3.5 14.2,9.45 20.55,9.7 15.55,13.65 17.3,19.8 12,16.25 6.7,19.8 8.45,13.65 3.45,9.7 9.8,9.45"
      fill={BLUE}
      stroke={BLUE}
      strokeWidth="1"
      strokeLinejoin="round"
    />
  ),
  heart: (
    <path d="M12 20.5s-7-4.5-9.5-9A5 5 0 0 1 12 6a5 5 0 0 1 9.5 5.5c-2.5 4.5-9.5 9-9.5 9z" fill={RED} />
  ),
  fish: (
    <>
      <ellipse cx="10" cy="12" rx="7" ry="4.6" fill={BLUE} />
      <path d="M15.5 12L21.5 7.5V16.5Z" fill={BLUE} strokeLinejoin="round" />
      <circle cx="6.6" cy="11" r="1.1" fill={PAPER} />
    </>
  ),
  apple: (
    <>
      <path
        d="M12 8.5c-2-1.5-7.5-1.5-7.5 4.5 0 4 3 8 5 8 1 0 1.5-.5 2.5-.5s1.5.5 2.5.5c2 0 5-4 5-8 0-6-5.5-6-7.5-4.5z"
        fill={RED}
      />
      <path d="M12 8.5V4.5" stroke={INK} strokeWidth="1.5" strokeLinecap="round" />
      <path d="M12.5 5.5c1-2 3-2.6 4.6-2.1-.5 1.6-2.6 2.6-4.6 2.1z" fill={INK} />
    </>
  ),
  flower: (
    <>
      {ring(5, 4.6).map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="3.6" fill={RED} />
      ))}
      <circle cx="12" cy="12" r="2.6" fill={INK} />
    </>
  ),
  boat: (
    <>
      <path d="M12 3.5V15" stroke={INK} strokeWidth="1.5" strokeLinecap="round" />
      <path d="M13.2 4.5L19 13.5H13.2Z" fill={BLUE} />
      <path d="M2.5 15.5H21.5L18 20.5H6Z" fill={BLUE} />
    </>
  ),
};

export function SignIcon({ sign, size = 48 }: { sign: Sign; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" role="img" aria-label={SIGN_NAMES[sign]}>
      {DRAWINGS[sign]}
    </svg>
  );
}
