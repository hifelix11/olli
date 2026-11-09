import { loadSession, saveSession, type Session } from "../storage";

export type Child = { id: string; name: string };

export type Task = {
  id: string;
  competency: string;
  title: string;
  kind: string;
  level: string;
  prompt: string;
  operands: Record<string, number | string>;
  options: (number | string)[] | null;
  representations: string[];
  placement: boolean;
};

export type AnswerResult = {
  correct: boolean;
  answer: number | string;
  p_known: number;
  backtracked_to: string | null;
};

export type MasteryStatus = "mastered" | "in_progress" | "not_started";

export type MasteryRow = {
  competency: string;
  title: string;
  area: string;
  p_known: number;
  status: MasteryStatus;
  practicable: boolean;
};

/** Stand gegenüber dem Lehrplan: Ziel bis Ende der Jahrgangsstufe. */
export type Progress = {
  curriculum: string;
  grade: number;
  goal: number;
  checkable: number;
  mastered: number;
  in_progress: number;
  placement_done: boolean;
};

const BASE: string = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

/** Fehler vom Backend. `code` ist der Fehlercode, etwa `invalid_credentials`. */
export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string) {
    super(`${status}: ${code}`);
    this.status = status;
    this.code = code;
  }
}

let session = loadSession();
let refreshing: Promise<boolean> | null = null;
let onSignOut = () => {};

function setSession(next: Session | null): void {
  session = next;
  saveSession(next);
}

function signOut(): void {
  setSession(null);
  onSignOut();
}

function send(path: string, init?: RequestInit): Promise<Response> {
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (session) headers.authorization = `Bearer ${session.access_token}`;
  return fetch(BASE + path, { ...init, headers });
}

async function fail(res: Response): Promise<never> {
  const body = (await res.json().catch(() => null)) as { detail?: unknown } | null;
  throw new ApiError(res.status, typeof body?.detail === "string" ? body.detail : res.statusText);
}

/** Neue Tokens holen. Parallele Aufrufe teilen sich eine Anfrage. */
function refresh(token: string): Promise<boolean> {
  refreshing ??= send("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: token }),
  })
    .then(async (res) => {
      if (res.ok) setSession((await res.json()) as Session);
      else if (res.status === 401) signOut();
      return res.ok;
    })
    .finally(() => {
      refreshing = null;
    });
  return refreshing;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res = await send(path, init);
  if (res.status === 401 && session && (await refresh(session.refresh_token))) {
    res = await send(path, init);
  }
  if (!res.ok) return fail(res);
  return (await res.json()) as T;
}

const post = <T>(path: string, body: unknown) =>
  request<T>(path, { method: "POST", body: JSON.stringify(body) });

export const auth = {
  signedIn: () => session !== null,
  /** Meldet, wenn die Anmeldung endet: abgemeldet oder abgelaufen. */
  onSignOut: (listener: () => void) => {
    onSignOut = listener;
  },
  login: async (email: string, password: string) => {
    setSession(await post<Session>("/auth/login", { email, password }));
  },
  /** false: Das Konto muss erst per E-Mail bestätigt werden. */
  signup: async (email: string, password: string) => {
    const next = await post<Session | null>("/auth/signup", { email, password });
    if (next) setSession(next);
    return next !== null;
  },
  logout: signOut,
};

export const api = {
  children: () => request<Child[]>("/children"),
  createChild: (name: string) => post<Child>("/children", { name }),
  nextTask: (childId: string) => request<Task | null>(`/children/${childId}/next-task`),
  answer: (childId: string, taskId: string, answer: number | string) =>
    post<AnswerResult>(`/children/${childId}/answers`, { task_id: taskId, answer }),
  mastery: (childId: string) => request<MasteryRow[]>(`/children/${childId}/mastery`),
  progress: (childId: string) => request<Progress>(`/children/${childId}/progress`),
};
