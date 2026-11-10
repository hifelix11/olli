import type { ReactNode } from "react";

/** Symbole statt Wörter: Ein Kind in der ersten Jahrgangsstufe liest noch nicht. */
export type IconName = "home" | "next" | "check" | "play" | "speaker";

const PATHS: Record<IconName, ReactNode> = {
  home: <path d="M3 11.5L12 4l9 7.5M5.5 9.5V20h13V9.5M10 20v-5.5h4V20" />,
  next: <path d="M4 12h15M13 6l6 6-6 6" />,
  check: <path d="M4.5 12.5l5 5L19.5 7" />,
  play: <path d="M7 4.5v15l12.5-7.5z" fill="currentColor" />,
  speaker: (
    <>
      <path d="M4 9v6h4l5 4V5L8 9H4z" fill="currentColor" />
      <path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a7.5 7.5 0 0 1 0 11" />
    </>
  ),
};

export function Icon({ name, size = 28 }: { name: IconName; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {PATHS[name]}
    </svg>
  );
}
