import type { Child } from "./api/client";

const KEY = "olli.children";

export function loadChildren(): Child[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "[]") as Child[];
  } catch {
    return [];
  }
}

export function saveChildren(children: Child[]): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(children));
  } catch {
    // Browser ohne Speicher: die Liste lebt dann nur für diese Sitzung.
  }
}
