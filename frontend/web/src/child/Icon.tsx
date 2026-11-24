import type { ReactNode } from "react";

/** Symbole statt Wörter: Ein Kind in der ersten Jahrgangsstufe liest noch nicht. */
export type IconName = "home" | "next" | "check" | "play" | "speaker" | "erase" | "lock";

const PATHS: Record<IconName, ReactNode> = {
  home: <path d="M3.5 11L12 4l8.5 7M6 9.5V19a1 1 0 0 0 1 1h3.5v-5h3v5H17a1 1 0 0 0 1-1V9.5" />,
  next: <path d="M4.5 12h14M13 6l6 6-6 6" />,
  check: <path d="M4.5 12.5l5 5L19.5 7" />,
  play: <path d="M8 5.2v13.6a1 1 0 0 0 1.5.9l10.6-6.8a1 1 0 0 0 0-1.8L9.5 4.3A1 1 0 0 0 8 5.2z" fill="currentColor" />,
  speaker: (
    <>
      <path d="M4 9.5v5h3.5l5 4.5V5L7.5 9.5H4z" fill="currentColor" />
      <path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a7.5 7.5 0 0 1 0 11" />
    </>
  ),
  // Radiergummi: Kinder korrigieren mit dem Radierer, nicht mit "Rückgängig".
  erase: (
    <>
      <path d="M14.2 4.6l5.2 5.2a1.5 1.5 0 0 1 0 2.1L12 19.3H8.3l-3.7-3.7a1.5 1.5 0 0 1 0-2.1l7.5-7.5a1.5 1.5 0 0 1 2.1 0z" />
      <path d="M8.6 9l6.4 6.4M12 19.3h8" />
    </>
  ),
  lock: (
    <>
      <rect x="5" y="10.5" width="14" height="10" rx="2.5" />
      <path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5" />
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
      strokeWidth="2.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {PATHS[name]}
    </svg>
  );
}
