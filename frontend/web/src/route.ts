import { useSyncExternalStore } from "react";

/** Wo man in der App ist. Steht in der Adresse, damit Neuladen dort bleibt. */
export type Route = { name: "start" } | { name: "practice"; childId: string } | { name: "parent" };

/** null: Adresse unbekannt. */
function parse(path: string): Route | null {
  if (path === "/") return { name: "start" };
  if (path === "/parent") return { name: "parent" };
  const match = /^\/practice\/([\w-]+)$/.exec(path);
  return match ? { name: "practice", childId: match[1] } : null;
}

function path(route: Route): string {
  if (route.name === "practice") return `/practice/${route.childId}`;
  return route.name === "parent" ? "/parent" : "/";
}

const listeners = new Set<() => void>();

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  window.addEventListener("popstate", listener);
  return () => {
    listeners.delete(listener);
    window.removeEventListener("popstate", listener);
  };
}

/** replace: ersetzt den Eintrag im Verlauf, etwa bei einer Umleitung. */
export function navigate(route: Route, replace = false): void {
  history[replace ? "replaceState" : "pushState"](null, "", path(route));
  listeners.forEach((listener) => listener());
}

export function useRoute(): Route | null {
  return parse(useSyncExternalStore(subscribe, () => location.pathname));
}
