import type { Task } from "../api/client";

/** Plättchen für das Zwanzigerfeld: rot, blau, weggenommen, noch leer. */
export type Counters = { red: number; blue: number; removed: number; empty: number };

const none: Counters = { red: 0, blue: 0, removed: 0, empty: 0 };
const num = (task: Task, key: string) => Number(task.operands[key]);

/** null, wenn die Aufgabe ohne Zwanzigerfeld gezeigt wird. Zählaufgaben zeigen es immer. */
export function countersFor(task: Task): Counters | null {
  if (!task.representations.includes("twenty_field") && task.kind !== "count") return null;
  switch (task.kind) {
    case "count":
      return { ...none, red: num(task, "n") };
    case "addition":
      return { ...none, red: num(task, "a"), blue: num(task, "b") };
    case "subtraction":
      return { ...none, red: num(task, "a") - num(task, "b"), removed: num(task, "b") };
    case "missing_number":
      if (task.operands.form !== "a+_=c") return null;
      return { ...none, red: num(task, "a"), empty: num(task, "c") - num(task, "a") };
    case "double_half":
      return { ...none, red: num(task, "value") };
    case "even_odd":
      return { ...none, red: num(task, "n") };
    default:
      return null;
  }
}
