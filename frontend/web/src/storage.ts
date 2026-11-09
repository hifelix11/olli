/** Tokens des Elternkontos. Nur das Backend prüft sie. */
export type Session = { access_token: string; refresh_token: string };

const KEY = "olli.session";

export function loadSession(): Session | null {
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "null") as Session | null;
  } catch {
    return null;
  }
}

export function saveSession(session: Session | null): void {
  try {
    if (session) localStorage.setItem(KEY, JSON.stringify(session));
    else localStorage.removeItem(KEY);
  } catch {
    // Browser ohne Speicher: die Anmeldung gilt dann nur für diese Sitzung.
  }
}
