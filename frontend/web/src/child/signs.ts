import type { Sign } from "../api/client";

/** Reihenfolge wie im Elternbereich. Jedes Zeichen in Plättchenrot oder -blau. */
export const SIGNS: Sign[] = ["sun", "moon", "star", "heart", "fish", "apple", "flower", "boat"];

export const SIGN_NAMES: Record<Sign, string> = {
  sun: "Sonne",
  moon: "Mond",
  star: "Stern",
  heart: "Herz",
  fish: "Fisch",
  apple: "Apfel",
  flower: "Blume",
  boat: "Boot",
};

/** Vorschlag: das erste Zeichen, das noch kein Geschwisterkind hat. */
export function freeSign(taken: Sign[]): Sign {
  return SIGNS.find((s) => !taken.includes(s)) ?? SIGNS[0];
}
