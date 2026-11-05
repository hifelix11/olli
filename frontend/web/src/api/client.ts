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

const BASE: string = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    ...init,
    headers: { "content-type": "application/json" },
  });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return (await res.json()) as T;
}

export const api = {
  createChild: (name: string) =>
    request<Child>("/children", { method: "POST", body: JSON.stringify({ name }) }),
  nextTask: (childId: string) => request<Task | null>(`/children/${childId}/next-task`),
  answer: (childId: string, taskId: string, answer: number | string) =>
    request<AnswerResult>(`/children/${childId}/answers`, {
      method: "POST",
      body: JSON.stringify({ task_id: taskId, answer }),
    }),
  mastery: (childId: string) => request<MasteryRow[]>(`/children/${childId}/mastery`),
};
